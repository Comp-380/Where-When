// State Management
const state = {
  token: localStorage.getItem("token") || null,
  currentUser: null,
  currentCalDate: new Date(),
  selectedDateStr: null,
  userAvailabilities: [],
};

// DOM Elements
const authSection = document.getElementById("auth-section");
const dashboardSection = document.getElementById("dashboard-section");

// Tab / View Elements
const tabSignupBtn = document.getElementById("tab-signup-btn");
const tabLoginBtn = document.getElementById("tab-login-btn");
const signupView = document.getElementById("signup-view");
const loginView = document.getElementById("login-view");
const forgotView = document.getElementById("forgot-view");
const resetView = document.getElementById("reset-view");
const linkToLogin = document.getElementById("link-to-login");
const linkToSignup = document.getElementById("link-to-signup");
const btnForgotPassword = document.getElementById("btn-forgot-password");
const linkFpToLogin = document.getElementById("link-fp-to-login");
const linkRpToLogin = document.getElementById("link-rp-to-login");

// Signup Form Elements
const signupForm = document.getElementById("signup-form");
const suUsername = document.getElementById("su-username");
const suEmail = document.getElementById("su-email");
const suFullName = document.getElementById("su-fullname");
const suPassword = document.getElementById("su-password");
const suConfirmPassword = document.getElementById("su-confirm-password");
const suTerms = document.getElementById("su-terms");
const btnSignup = document.getElementById("btn-signup");
const valIconUsername = document.getElementById("val-icon-username");
const valIconEmail = document.getElementById("val-icon-email");
const confirmMatchHint = document.getElementById("confirm-match-hint");

// Password Meter & Requirements Elements (Signup)
const passwordMeterFill = document.getElementById("password-meter-fill");
const passwordStrengthText = document.getElementById("password-strength-text");
const reqLen = document.getElementById("req-len");
const reqUpper = document.getElementById("req-upper");
const reqLower = document.getElementById("req-lower");
const reqNum = document.getElementById("req-num");
const reqSpecial = document.getElementById("req-special");

// Login Form Elements
const loginForm = document.getElementById("login-form");
const liIdentifier = document.getElementById("li-identifier");
const liPassword = document.getElementById("li-password");
const btnLogin = document.getElementById("btn-login");
const resendSection = document.getElementById("resend-section");
const btnResendVerification = document.getElementById("btn-resend-verification");

// Forgot Password Elements
const forgotForm = document.getElementById("forgot-form");
const fpEmail = document.getElementById("fp-email");
const valIconFpEmail = document.getElementById("val-icon-fp-email");
const btnForgot = document.getElementById("btn-forgot");

// Reset Password Elements
const resetForm = document.getElementById("reset-form");
const rpToken = document.getElementById("rp-token");
const rpPassword = document.getElementById("rp-password");
const rpConfirmPassword = document.getElementById("rp-confirm-password");
const rpPasswordMeterFill = document.getElementById("rp-password-meter-fill");
const rpPasswordStrengthText = document.getElementById("rp-password-strength-text");
const rpReqLen = document.getElementById("rp-req-len");
const rpReqUpper = document.getElementById("rp-req-upper");
const rpReqLower = document.getElementById("rp-req-lower");
const rpReqNum = document.getElementById("rp-req-num");
const rpReqSpecial = document.getElementById("rp-req-special");
const rpConfirmMatchHint = document.getElementById("rp-confirm-match-hint");
const btnReset = document.getElementById("btn-reset");

// Dashboard Elements
const dashAvatarImg = document.getElementById("dash-avatar-img");
const avatarInput = document.getElementById("avatar-input");
const dashAvatar = document.getElementById("dash-avatar");
const dashGreetingName = document.getElementById("dash-greeting-name");
const dashGreetingHandle = document.getElementById("dash-greeting-handle");
const dashId = document.getElementById("dash-id");
const dashUsername = document.getElementById("dash-username");
const dashEmail = document.getElementById("dash-email");
const dashFullname = document.getElementById("dash-fullname");
const dashJoined = document.getElementById("dash-joined");
const dbUsersTbody = document.getElementById("db-users-tbody");
const btnRefreshUsers = document.getElementById("btn-refresh-users");
const btnLogout = document.getElementById("btn-logout");
const toastContainer = document.getElementById("toast-container");
const calPrevBtn = document.getElementById("cal-prev-btn");
const calNextBtn = document.getElementById("cal-next-btn");
const calMonthYear = document.getElementById("cal-month-year");
const calDaysGrid = document.getElementById("cal-days-grid");
const calSelectedDateText = document.getElementById("cal-selected-date-text");
const availabilityForm = document.getElementById("availability-form");
const availDateInput = document.getElementById("avail-date-input");
const availTitle = document.getElementById("avail-title");
const availStart = document.getElementById("avail-start");
const availEnd = document.getElementById("avail-end");
const dateSlotsList = document.getElementById("date-slots-list");

// Toast Notification Utility
function showToast(message, type = "info", duration = 4000) {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(40px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Tab Switching (Default tab: login)
function switchTab(target) {
  signupView.classList.remove("active");
  loginView.classList.remove("active");
  if (forgotView) forgotView.classList.remove("active");
  if (resetView) resetView.classList.remove("active");

  tabSignupBtn.classList.remove("active");
  tabSignupBtn.setAttribute("aria-selected", "false");
  tabLoginBtn.classList.remove("active");
  tabLoginBtn.setAttribute("aria-selected", "false");

  if (target === "signup") {
    tabSignupBtn.classList.add("active");
    tabSignupBtn.setAttribute("aria-selected", "true");
    signupView.classList.add("active");
  } else if (target === "login") {
    tabLoginBtn.classList.add("active");
    tabLoginBtn.setAttribute("aria-selected", "true");
    loginView.classList.add("active");
  } else if (target === "forgot") {
    if (forgotView) forgotView.classList.add("active");
  } else if (target === "reset") {
    if (resetView) resetView.classList.add("active");
  }
}

tabSignupBtn.addEventListener("click", () => switchTab("signup"));
tabLoginBtn.addEventListener("click", () => switchTab("login"));
linkToLogin.addEventListener("click", () => switchTab("login"));
linkToSignup.addEventListener("click", () => switchTab("signup"));

if (btnForgotPassword) {
  btnForgotPassword.addEventListener("click", () => {
    const currentId = liIdentifier.value.trim();
    if (currentId.includes("@") && fpEmail) {
      fpEmail.value = currentId;
      validateFpEmail(currentId);
    }
    switchTab("forgot");
  });
}

if (linkFpToLogin) linkFpToLogin.addEventListener("click", () => switchTab("login"));
if (linkRpToLogin) linkRpToLogin.addEventListener("click", () => switchTab("login"));

// Password Visibility Toggles
document.querySelectorAll(".toggle-password").forEach((button) => {
  button.addEventListener("click", () => {
    const targetId = button.getAttribute("data-target");
    const input = document.getElementById(targetId);
    const eyeOpen = button.querySelector(".eye-open");
    const eyeClosed = button.querySelector(".eye-closed");

    if (input.type === "password") {
      input.type = "text";
      eyeOpen.classList.add("hidden");
      eyeClosed.classList.remove("hidden");
    } else {
      input.type = "password";
      eyeOpen.classList.remove("hidden");
      eyeClosed.classList.add("hidden");
    }
  });
});

// Live Form Validation Logic
function validateUsername(value) {
  const clean = value.trim();
  const valid = /^[a-zA-Z0-9_-]{3,30}$/.test(clean);

  if (!clean) {
    suUsername.classList.remove("valid-input", "invalid-input");
    valIconUsername.textContent = "";
    return false;
  }

  if (valid) {
    suUsername.classList.add("valid-input");
    suUsername.classList.remove("invalid-input");
    valIconUsername.textContent = "✓";
    valIconUsername.style.color = "#10b981";
  } else {
    suUsername.classList.add("invalid-input");
    suUsername.classList.remove("valid-input");
    valIconUsername.textContent = "✕";
    valIconUsername.style.color = "#ef4444";
  }
  return valid;
}

function validateEmail(value) {
  const clean = value.trim();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const valid = emailRegex.test(clean);

  if (!clean) {
    suEmail.classList.remove("valid-input", "invalid-input");
    valIconEmail.textContent = "";
    return false;
  }

  if (valid) {
    suEmail.classList.add("valid-input");
    suEmail.classList.remove("invalid-input");
    valIconEmail.textContent = "✓";
    valIconEmail.style.color = "#10b981";
  } else {
    suEmail.classList.add("invalid-input");
    suEmail.classList.remove("valid-input");
    valIconEmail.textContent = "✕";
    valIconEmail.style.color = "#ef4444";
  }
  return valid;
}

function evaluatePassword(pwd) {
  const hasLen = pwd.length >= 8;
  const hasUpper = /[A-Z]/.test(pwd);
  const hasLower = /[a-z]/.test(pwd);
  const hasNum = /\d/.test(pwd);
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(pwd);

  updateReqItem(reqLen, hasLen);
  updateReqItem(reqUpper, hasUpper);
  updateReqItem(reqLower, hasLower);
  updateReqItem(reqNum, hasNum);
  updateReqItem(reqSpecial, hasSpecial);

  const checks = [hasLen, hasUpper, hasLower, hasNum, hasSpecial];
  const passedCount = checks.filter(Boolean).length;

  let width = "0%";
  let color = "#ef4444";
  let label = "Too short";

  if (pwd.length === 0) {
    width = "0%";
    label = "Too short";
  } else if (passedCount <= 2) {
    width = "25%";
    color = "#ef4444";
    label = "Weak";
  } else if (passedCount === 3) {
    width = "50%";
    color = "#f59e0b";
    label = "Fair";
  } else if (passedCount === 4) {
    width = "75%";
    color = "#3b82f6";
    label = "Good";
  } else if (passedCount === 5) {
    width = "100%";
    color = "#10b981";
    label = "Strong";
  }

  passwordMeterFill.style.width = width;
  passwordMeterFill.style.backgroundColor = color;
  passwordStrengthText.textContent = label;
  passwordStrengthText.style.color = color;

  return passedCount === 5;
}

function updateReqItem(element, isMet) {
  const bullet = element.querySelector(".req-bullet");
  if (isMet) {
    element.classList.add("met");
    bullet.textContent = "✓";
  } else {
    element.classList.remove("met");
    bullet.textContent = "•";
  }
}

function checkPasswordMatch() {
  const pwd = suPassword.value;
  const confirm = suConfirmPassword.value;

  if (!confirm) {
    confirmMatchHint.textContent = "";
    confirmMatchHint.className = "field-hint";
    suConfirmPassword.classList.remove("valid-input", "invalid-input");
    return false;
  }

  if (pwd === confirm) {
    confirmMatchHint.textContent = "✓ Passwords match";
    confirmMatchHint.className = "field-hint success";
    suConfirmPassword.classList.add("valid-input");
    suConfirmPassword.classList.remove("invalid-input");
    return true;
  } else {
    confirmMatchHint.textContent = "✕ Passwords do not match";
    confirmMatchHint.className = "field-hint error";
    suConfirmPassword.classList.add("invalid-input");
    suConfirmPassword.classList.remove("valid-input");
    return false;
  }
}

// Event Listeners for Live Form Feedback
suUsername.addEventListener("input", (e) => validateUsername(e.target.value));
suEmail.addEventListener("input", (e) => validateEmail(e.target.value));
suPassword.addEventListener("input", (e) => {
  evaluatePassword(e.target.value);
  if (suConfirmPassword.value) checkPasswordMatch();
});
suConfirmPassword.addEventListener("input", checkPasswordMatch);

// Signup Form Submit Handler
signupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = suUsername.value.trim();
  const email = suEmail.value.trim();
  const fullName = suFullName.value.trim() || null;
  const password = suPassword.value;
  const confirmPassword = suConfirmPassword.value;

  if (!validateUsername(username)) {
    showToast("Please enter a valid username (3-30 chars, alphanumeric).", "error");
    suUsername.focus();
    return;
  }
  if (!validateEmail(email)) {
    showToast("Please enter a valid email address.", "error");
    suEmail.focus();
    return;
  }
  if (!evaluatePassword(password)) {
    showToast("Please ensure password satisfies all strength criteria.", "error");
    suPassword.focus();
    return;
  }
  if (password !== confirmPassword) {
    showToast("Passwords do not match.", "error");
    suConfirmPassword.focus();
    return;
  }
  if (!suTerms.checked) {
    showToast("Please agree to the Terms of Service to continue.", "error");
    return;
  }

  setButtonLoading(btnSignup, true);
  try {
    const response = await fetch("/api/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username,
        email,
        full_name: fullName,
        password,
        confirm_password: confirmPassword,
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      const errMsg = Array.isArray(data.detail)
        ? data.detail.map((d) => d.msg).join(", ")
        : data.detail || "Registration failed.";
      throw new Error(errMsg);
    }
    showToast(data.message || "Account created! Check your email to verify before signing in.", "success", 7000);
    signupForm.reset();
    evaluatePassword("");
    liIdentifier.value = username;
    switchTab("login");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setButtonLoading(btnSignup, false);
  }
});

// Login Form Submit Handler
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const identifier = liIdentifier.value.trim();
  const password = liPassword.value;

  if (!identifier) {
    showToast("Please enter your username or email.", "error");
    liIdentifier.focus();
    return;
  }
  if (!password) {
    showToast("Please enter your password.", "error");
    liPassword.focus();
    return;
  }

  setButtonLoading(btnLogin, true);
  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier, password }),
    });

    if (!(response.headers.get("content-type") || "").includes("application/json")) {
      throw new Error("The server could not process your login. Please try again shortly.");
    }

    const data = await response.json();
    if (!response.ok) {
      if (response.status === 403 && data.detail && data.detail.toLowerCase().includes("verify")) {
        showToast(data.detail, "error", 7000);
        if (resendSection) resendSection.classList.remove("hidden");
        return;
      }
      throw new Error(data.detail || "Login failed.");
    }
    showToast("Signed in successfully!", "success");
    handleAuthSuccess(data);
    loginForm.reset();
    if (resendSection) resendSection.classList.add("hidden");
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setButtonLoading(btnLogin, false);
  }
});

// Resend Verification Email Listener
if (btnResendVerification) {
  btnResendVerification.addEventListener("click", async () => {
    const identifier = liIdentifier.value.trim();
    if (!identifier || !identifier.includes("@")) {
      showToast("Please enter your email into the Sign In field above.", "error");
      liIdentifier.focus();
      return;
    }
    try {
      const res = await fetch("/api/auth/resend-verification", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: identifier }),
      });
      const data = await res.json();
      showToast(data.message || "Verification email dispatched.", "info", 5000);
    } catch (e) {
      showToast("Could not send verification request.", "error");
    }
  });
}

// Live Validation for Forgot Password Email
function validateFpEmail(value) {
  const clean = value.trim();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const valid = emailRegex.test(clean);

  if (!clean) {
    fpEmail.classList.remove("valid-input", "invalid-input");
    valIconFpEmail.textContent = "";
    return false;
  }

  if (valid) {
    fpEmail.classList.add("valid-input");
    fpEmail.classList.remove("invalid-input");
    valIconFpEmail.textContent = "✓";
    valIconFpEmail.style.color = "#10b981";
  } else {
    fpEmail.classList.add("invalid-input");
    fpEmail.classList.remove("valid-input");
    valIconFpEmail.textContent = "✕";
    valIconFpEmail.style.color = "#ef4444";
  }
  return valid;
}

if (fpEmail) {
  fpEmail.addEventListener("input", (e) => validateFpEmail(e.target.value));
}

// Forgot Password Form Submit Handler
if (forgotForm) {
  forgotForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = fpEmail.value.trim();
    if (!validateFpEmail(email)) {
      showToast("Please enter a valid email address.", "error");
      fpEmail.focus();
      return;
    }

    setButtonLoading(btnForgot, true);
    try {
      const response = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to request password reset.");
      }
      showToast(
        data.message || "If an account with this email exists, a password reset link has been sent.",
        "success",
        7000
      );
      forgotForm.reset();
      fpEmail.classList.remove("valid-input", "invalid-input");
      valIconFpEmail.textContent = "";
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setButtonLoading(btnForgot, false);
    }
  });
}

// Live Evaluation for Reset Password
function evaluateResetPassword(pwd) {
  const hasLen = pwd.length >= 8;
  const hasUpper = /[A-Z]/.test(pwd);
  const hasLower = /[a-z]/.test(pwd);
  const hasNum = /\d/.test(pwd);
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(pwd);

  updateReqItem(rpReqLen, hasLen);
  updateReqItem(rpReqUpper, hasUpper);
  updateReqItem(rpReqLower, hasLower);
  updateReqItem(rpReqNum, hasNum);
  updateReqItem(rpReqSpecial, hasSpecial);

  const checks = [hasLen, hasUpper, hasLower, hasNum, hasSpecial];
  const passedCount = checks.filter(Boolean).length;

  let width = "0%";
  let color = "#ef4444";
  let label = "Too short";

  if (pwd.length === 0) {
    width = "0%";
    label = "Too short";
  } else if (passedCount <= 2) {
    width = "25%";
    color = "#ef4444";
    label = "Weak";
  } else if (passedCount === 3) {
    width = "50%";
    color = "#f59e0b";
    label = "Fair";
  } else if (passedCount === 4) {
    width = "75%";
    color = "#3b82f6";
    label = "Good";
  } else if (passedCount === 5) {
    width = "100%";
    color = "#10b981";
    label = "Strong";
  }

  rpPasswordMeterFill.style.width = width;
  rpPasswordMeterFill.style.backgroundColor = color;
  rpPasswordStrengthText.textContent = label;
  rpPasswordStrengthText.style.color = color;

  return passedCount === 5;
}

function checkResetPasswordMatch() {
  const pwd = rpPassword.value;
  const confirm = rpConfirmPassword.value;

  if (!confirm) {
    rpConfirmMatchHint.textContent = "";
    rpConfirmMatchHint.className = "field-hint";
    rpConfirmPassword.classList.remove("valid-input", "invalid-input");
    return false;
  }

  if (pwd === confirm) {
    rpConfirmMatchHint.textContent = "✓ Passwords match";
    rpConfirmMatchHint.className = "field-hint success";
    rpConfirmPassword.classList.add("valid-input");
    rpConfirmPassword.classList.remove("invalid-input");
    return true;
  } else {
    rpConfirmMatchHint.textContent = "✕ Passwords do not match";
    rpConfirmMatchHint.className = "field-hint error";
    rpConfirmPassword.classList.add("invalid-input");
    rpConfirmPassword.classList.remove("valid-input");
    return false;
  }
}

if (rpPassword) {
  rpPassword.addEventListener("input", (e) => {
    evaluateResetPassword(e.target.value);
    if (rpConfirmPassword && rpConfirmPassword.value) checkResetPasswordMatch();
  });
}

if (rpConfirmPassword) {
  rpConfirmPassword.addEventListener("input", checkResetPasswordMatch);
}

// Reset Password Form Submit Handler
if (resetForm) {
  resetForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const token = rpToken.value.trim();
    const password = rpPassword.value;
    const confirmPassword = rpConfirmPassword.value;

    if (!token) {
      showToast("Reset token is missing. Please use the link sent to your email.", "error");
      return;
    }
    if (!evaluateResetPassword(password)) {
      showToast("Password does not meet all security requirements.", "error");
      rpPassword.focus();
      return;
    }
    if (password !== confirmPassword) {
      showToast("Passwords do not match.", "error");
      rpConfirmPassword.focus();
      return;
    }

    setButtonLoading(btnReset, true);
    try {
      const response = await fetch("/api/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token,
          password,
          confirm_password: confirmPassword,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Password reset failed.");
      }
      showToast(
        data.message || "Your password has been successfully reset! You can now log in.",
        "success",
        7000
      );
      resetForm.reset();
      evaluateResetPassword("");
      switchTab("login");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setButtonLoading(btnReset, false);
    }
  });
}

// Handle Successful Authentication
function handleAuthSuccess(authData) {
  state.token = authData.access_token;
  state.currentUser = authData.user;
  localStorage.setItem("token", authData.access_token);
  renderDashboard(authData.user);
  loadDatabaseUsers();
  loadAvailabilities();
}

// Dashboard Rendering
function renderDashboard(user) {
  authSection.classList.add("hidden");
  dashboardSection.classList.remove("hidden");

  const displayName = user.full_name || user.username;
  if (user.avatar_url) {
    dashAvatarImg.src = user.avatar_url;
    dashAvatarImg.classList.remove("hidden");
    dashAvatar.classList.add("hidden");
  } else {
    dashAvatar.textContent = (displayName[0] || "U").toUpperCase();
    dashAvatar.classList.remove("hidden");
    dashAvatarImg.classList.add("hidden");
  }

  dashGreetingName.textContent = `Welcome, ${displayName}!`;
  dashGreetingHandle.textContent = `@${user.username}`;
  dashId.textContent = `#${user.id}`;
  dashUsername.textContent = user.username;
  dashEmail.textContent = user.email;
  dashFullname.textContent = user.full_name || "Not provided";

  const dateObj = new Date(user.created_at);
  dashJoined.textContent = dateObj.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Fetch Registered Users from Database
async function loadDatabaseUsers() {
  dbUsersTbody.innerHTML = `<tr><td colspan="5" class="table-loading">Loading users from SQLite...</td></tr>`;
  try {
    const response = await fetch("/api/users");
    if (!response.ok) throw new Error("Failed to fetch database users");
    const users = await response.json();

    if (users.length === 0) {
      dbUsersTbody.innerHTML = `<tr><td colspan="5" class="table-loading">No users found in database.</td></tr>`;
      return;
    }

    dbUsersTbody.innerHTML = users
      .map((u) => {
        const d = new Date(u.created_at);
        const formatted = d.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        });
        return `
        <tr>
          <td><strong>#${u.id}</strong></td>
          <td>@${escapeHtml(u.username)}</td>
          <td>${escapeHtml(u.email)}</td>
          <td>${escapeHtml(u.full_name || "")}</td>
          <td>${formatted}</td>
        </tr>
      `;
      })
      .join("");
  } catch (err) {
    dbUsersTbody.innerHTML = `<tr><td colspan="5" class="table-loading" style="color: #f87171;">Error loading users from database</td></tr>`;
  }
}

if (btnRefreshUsers) {
  btnRefreshUsers.addEventListener("click", loadDatabaseUsers);
}

// Logout Handler
btnLogout.addEventListener("click", () => {
  state.token = null;
  state.currentUser = null;
  localStorage.removeItem("token");
  dashboardSection.classList.add("hidden");
  authSection.classList.remove("hidden");
  switchTab("login");
  showToast("You have been signed out.", "info");
});

// Helper: Button Loading State
function setButtonLoading(button, isLoading) {
  const textSpan = button.querySelector(".btn-text");
  const spinner = button.querySelector(".spinner");
  if (isLoading) {
    button.disabled = true;
    textSpan.classList.add("hidden");
    spinner.classList.remove("hidden");
  } else {
    button.disabled = false;
    textSpan.classList.remove("hidden");
    spinner.classList.add("hidden");
  }
}

// Helper: HTML escaping
function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Check Email Verification URL Parameter
async function checkEmailVerificationParam() {
  const params = new URLSearchParams(window.location.search);
  if (params.get("reset_token") || window.location.pathname.includes("reset-password")) return;

  const token = params.get("token");
  if (!token) return;

  try {
    const res = await fetch(`/api/auth/verify?token=${encodeURIComponent(token)}`);
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || "Email verified! You can now sign in.", "success", 6000);
      switchTab("login");
    } else {
      showToast(data.detail || "Verification link is invalid or expired.", "error", 6000);
    }
  } catch (err) {
    showToast("Failed to connect to verification server.", "error");
  } finally {
    window.history.replaceState({}, document.title, window.location.pathname);
  }
}

// Check Password Reset URL Parameter
async function checkPasswordResetParam() {
  const params = new URLSearchParams(window.location.search);
  const resetToken =
    params.get("reset_token") ||
    (window.location.pathname.includes("reset-password") ? params.get("token") : null);

  if (!resetToken) return;

  try {
    const res = await fetch(`/api/auth/verify-reset-token?token=${encodeURIComponent(resetToken)}`);
    const data = await res.json();
    if (res.ok) {
      if (rpToken) rpToken.value = resetToken;
      showToast("Reset token verified. Please enter your new password.", "info", 5000);
      switchTab("reset");
    } else {
      showToast(data.detail || "Password reset link is invalid or expired.", "error", 7000);
      switchTab("login");
    }
  } catch (err) {
    showToast("Failed to connect to verification server.", "error");
  } finally {
    window.history.replaceState({}, document.title, window.location.pathname);
  }
}

// Initial Session Check
async function checkExistingSession() {
  if (!state.token) return;
  try {
    const response = await fetch("/api/auth/me", {
      headers: {
        Authorization: `Bearer ${state.token}`,
      },
    });
    if (response.ok) {
      const user = await response.json();
      state.currentUser = user;
      renderDashboard(user);
      loadDatabaseUsers();
      loadAvailabilities();
    } else {
      localStorage.removeItem("token");
      state.token = null;
    }
  } catch (e) {
    // Leave at Sign In on connection failure
  }
}

if (avatarInput) {
  avatarInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      showToast("Image must be smaller than 5MB", "error");
      avatarInput.value = "";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      showToast("Uploading avatar...", "info", 2000);
      const res = await fetch("/api/users/me/avatar", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${state.token}`,
        },
        body: formData,
      });

      const data = await response.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to upload avatar");
      }
      state.currentUser = data;
      renderDashboard(data);
      showToast("Profile picture updated!", "success");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      avatarInput.value = "";
    }
  });
}

// Boot application
switchTab("login");
checkEmailVerificationParam();
checkPasswordResetParam();
checkExistingSession();

// ==================== CALENDAR AVAILABILITY ====================
async function loadAvailabilities() {
  if (!state.token) return;
  try {
    const res = await fetch("/api/availability", {
      headers: { Authorization: `Bearer ${state.token}` }
    });
    if (res.ok) {
      state.userAvailabilities = await res.json();
      renderCalendar();
      if (state.selectedDateStr) renderSlotsForDate(state.selectedDateStr);
    }
  } catch (e) {
    console.error("Failed to load availabilities", e);
  }
}

function renderCalendar() {
  if (!calDaysGrid) return;
  const year = state.currentCalDate.getFullYear();
  const month = state.currentCalDate.getMonth();

  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  calMonthYear.textContent = `${monthNames[month]} ${year}`;

  calDaysGrid.innerHTML = "";

  const firstDayIndex = new Date(year, month, 1).getDay();
  const totalDays = new Date(year, month + 1, 0).getDate();

  for (let i = 0; i < firstDayIndex; i++) {
    const emptyCell = document.createElement("div");
    emptyCell.className = "cal-day-cell disabled";
    calDaysGrid.appendChild(emptyCell);
  }

  for (let day = 1; day <= totalDays; day++) {
    const cell = document.createElement("div");
    cell.className = "cal-day-cell";
    cell.textContent = day;

    const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

    if (state.userAvailabilities.some((a) => a.date === dateStr)) {
      cell.classList.add("has-slots");
    }
    if (state.selectedDateStr === dateStr) {
      cell.classList.add("selected");
    }

    cell.addEventListener("click", () => {
      document.querySelectorAll(".cal-day-cell").forEach((c) => c.classList.remove("selected"));
      cell.classList.add("selected");
      selectCalendarDate(dateStr);
    });

    calDaysGrid.appendChild(cell);
  }
}

function selectCalendarDate(dateStr) {
  state.selectedDateStr = dateStr;
  availDateInput.value = dateStr;
  availabilityForm.classList.remove("hidden");

  const [y, m, d] = dateStr.split("-");
  calSelectedDateText.textContent = `Slots for ${new Date(y, m - 1, d).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}`;
  renderSlotsForDate(dateStr);
}

function renderSlotsForDate(dateStr) {
  const slots = state.userAvailabilities.filter((a) => a.date === dateStr);
  if (slots.length === 0) {
    dateSlotsList.innerHTML = `<p class="cal-empty-slots">No slots scheduled for this day.</p>`;
    return;
  }

  dateSlotsList.innerHTML = slots
    .map(
      (s) => `
      <div class="slot-item">
        <div>
          <strong>${escapeHtml(s.title)}</strong>
          <div style="color: var(--text-muted); font-size: 0.72rem;">${s.start_time.slice(0, 5)} - ${s.end_time.slice(0, 5)}</div>
        </div>
        <button class="btn-del-slot" onclick="deleteSlot(${s.id})" title="Delete Slot">&times;</button>
      </div>
    `
    )
    .join("");
}

window.deleteSlot = async function (slotId) {
  try {
    const res = await fetch(`/api/availability/${slotId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${state.token}` }
    });
    if (!res.ok) throw new Error("Could not delete slot");
    showToast("Availability slot removed", "info");
    await loadAvailabilities();
  } catch (err) {
    showToast(err.message, "error");
  }
};

if (availabilityForm) {
  availabilityForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const dateVal = availDateInput.value;
    const startTime = availStart.value;
    const endTime = availEnd.value;
    const titleVal = availTitle.value.trim() || "Available";

    if (startTime >= endTime) {
      showToast("Start time must be before end time.", "error");
      return;
    }

    try {
      const res = await fetch("/api/availability", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${state.token}`
        },
        body: JSON.stringify({
          date: dateVal,
          start_time: startTime + ":00",
          end_time: endTime + ":00",
          title: titleVal
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to add slot");

      showToast("Slot added!", "success");
      await loadAvailabilities();
    } catch (err) {
      showToast(err.message, "error");
    }
  });
}

if (calPrevBtn) {
  calPrevBtn.addEventListener("click", () => {
    state.currentCalDate.setMonth(state.currentCalDate.getMonth() - 1);
    renderCalendar();
  });
}

if (calNextBtn) {
  calNextBtn.addEventListener("click", () => {
    state.currentCalDate.setMonth(state.currentCalDate.getMonth() + 1);
    renderCalendar();
  });
}

// ==================== EDIT & DELETE PROFILE ====================
const btnToggleEditProfile = document.getElementById("btn-toggle-edit-profile");
const editProfileForm = document.getElementById("edit-profile-form");
const btnCancelEdit = document.getElementById("btn-cancel-edit");
const editFullname = document.getElementById("edit-fullname");
const editUsername = document.getElementById("edit-username");
const btnDeleteAccount = document.getElementById("btn-delete-account");

if (btnToggleEditProfile) {
  btnToggleEditProfile.addEventListener("click", () => {
    if (state.currentUser) {
      editFullname.value = state.currentUser.full_name || "";
      editUsername.value = state.currentUser.username || "";
      editProfileForm.classList.toggle("hidden");
    }
  });
}

if (btnCancelEdit) {
  btnCancelEdit.addEventListener("click", () => {
    editProfileForm.classList.add("hidden");
  });
}

if (editProfileForm) {
  editProfileForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/users/me", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${state.token}`,
        },
        body: JSON.stringify({
          full_name: editFullname.value.trim(),
          username: editUsername.value.trim(),
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to update profile.");

      state.currentUser = data;
      renderDashboard(data);
      editProfileForm.classList.add("hidden");
      showToast("Profile updated successfully!", "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  });
}

if (btnDeleteAccount) {
  btnDeleteAccount.addEventListener("click", async () => {
    const confirmed = confirm("Are you sure you want to permanently delete your account?");
    if (!confirmed) return;

    try {
      const res = await fetch("/api/users/me", {
        method: "DELETE",
        headers: { Authorization: `Bearer ${state.token}` },
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to delete account.");

      showToast("Account deleted.", "info");
      btnLogout.click();
    } catch (err) {
      showToast(err.message, "error");
    }
  });
}

// ==================== CREATE GROUP (SCRUM-40) ====================
const createGroupForm = document.getElementById("create-group-form");
const groupNameInput = document.getElementById("group-name");
const groupDescInput = document.getElementById("group-desc");
const btnCreateGroup = document.getElementById("btn-create-group");

if (createGroupForm) {
  createGroupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = groupNameInput.value.trim();
    const description = groupDescInput.value.trim() || null;

    if (!name || name.length < 2) {
      showToast("Group name must be at least 2 characters.", "error");
      groupNameInput.focus();
      return;
    }

    setButtonLoading(btnCreateGroup, true);
    try {
      const response = await fetch("/api/groups", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${state.token}`,
        },
        body: JSON.stringify({ name, description }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to create group.");
      }

      showToast(`Group "${data.name}" created successfully!`, "success", 5000);
      createGroupForm.reset();
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setButtonLoading(btnCreateGroup, false);
    }
  });
}