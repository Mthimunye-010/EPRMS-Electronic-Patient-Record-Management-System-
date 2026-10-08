(() => {
  const page = document.querySelector("[data-session-timeout]");
  const modalElement = document.getElementById("sessionWarningModal");
  if (!page || !modalElement || !window.bootstrap) return;

  const timeoutSeconds = Number(page.dataset.sessionTimeout) || 900;
  const warningSeconds = Math.min(120, Math.floor(timeoutSeconds / 3));
  const keepaliveUrl = page.dataset.sessionKeepaliveUrl;
  const loginUrl = page.dataset.sessionLoginUrl;
  const countdown = document.getElementById("sessionCountdown");
  const modal = bootstrap.Modal.getOrCreateInstance(modalElement, { backdrop: "static", keyboard: false });
  let deadline = Date.now() + timeoutSeconds * 1000;
  let lastTouch = Date.now();
  let lastHeartbeat = Date.now();
  let inFlight = false;
  let expired = false;
  let activityTimer;

  const logout = () => {
    const form = document.getElementById("logoutForm");
    if (form) form.requestSubmit();
  };

  document.getElementById("sessionLogout")?.addEventListener("click", logout);
  const keepSession = async () => {
    if (inFlight || expired) return;
    inFlight = true;
    const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    try {
      const response = await fetch(keepaliveUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: { "X-CSRFToken": csrf || "", "X-Requested-With": "XMLHttpRequest" },
      });
      const payload = response.ok ? await response.json() : null;
      if (!payload?.ok) {
        expired = true;
        window.location.assign(loginUrl);
        return;
      }
      deadline = Date.now() + timeoutSeconds * 1000;
      lastTouch = Date.now();
      lastHeartbeat = Date.now();
      modal.hide();
    } catch {
      countdown.textContent = "Connection issue. Try again, or sign out.";
    } finally {
      inFlight = false;
    }
  };
  document.getElementById("sessionStaySignedIn")?.addEventListener("click", keepSession);

  const noteActivity = () => {
    lastTouch = Date.now();
    window.clearTimeout(activityTimer);
    activityTimer = window.setTimeout(() => {
      if (Date.now() - lastHeartbeat >= 20000) keepSession();
    }, 1200);
  };
  ["pointerdown", "keydown", "input", "touchstart"].forEach((eventName) => {
    document.addEventListener(eventName, noteActivity, { passive: true });
  });

  window.setInterval(async () => {
    if (expired) return;
    const remaining = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
    if (remaining === 0) {
      expired = true;
      logout();
      return;
    }
    if (remaining <= warningSeconds) {
      countdown.textContent = `You will be signed out in ${Math.floor(remaining / 60)}:${String(remaining % 60).padStart(2, "0")}.`;
      modal.show();
    }

    if (!inFlight && Date.now() - lastTouch < 30000 && Date.now() - lastHeartbeat >= 20000) keepSession();
  }, 1000);
})();
