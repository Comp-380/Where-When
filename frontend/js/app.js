// State Management
const state = {
  token: localStorage.getItem("token") || null,
  currentUser: null,
  currentCalDate: new Date(),
  selectedDateStr: null,
  userAvailabilities: [],
  userGroups: [],
  selectedGroup: null,
  currentGroupData: null,
  selectedMemberIds: new Set(),
  currentGroupPolls: {},
  currentGroupPollOptions: [],
};

// DOM Elements
const authSection = document.getElementById("auth-section");
const dashboardSection = document.getElementById("dashboard-section");

// Tab / View Elements (Auth)
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

// Dashboard Tabs Elements
const dashTabButtons = document.querySelectorAll(".dash-tab-btn");
const dashPanels = document.querySelectorAll(".dash-panel");
const dashGroupsBadge = document.getElementById("dash-groups-badge");

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

// Dashboard Header Elements
const dashAvatarImg = document.getElementById("dash-avatar-img");
const avatarInput = document.getElementById("avatar-input");
const dashAvatar = document.getElementById("dash-avatar");
const dashGreetingName = document.getElementById("dash-greeting-name");
const dashGreetingHandle = document.getElementById("dash-greeting-handle");
const dashId = document.getElementById("dash-id");
const dashUsername = document.getElementById("dash-username");
const dashEmail = document.getElementById("dash-email");
const dashFullname = document.getElementById("dash-fullname");
const dashStreet = document.getElementById("dash-street");
const dashState = document.getElementById("dash-state");
const dashZip = document.getElementById("dash-zip");
const dashDistance = document.getElementById("dash-distance");
const dashJoined = document.getElementById("dash-joined");
const btnLogout = document.getElementById("btn-logout");
const toastContainer = document.getElementById("toast-container");

// Calendar Availability Elements
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

// Groups Elements
const createGroupForm = document.getElementById("create-group-form");
const groupNameInput = document.getElementById("group-name");
const groupDescInput = document.getElementById("group-desc");
const btnCreateGroup = document.getElementById("btn-create-group");
const groupsListContainer = document.getElementById("groups-list-container");
const btnRefreshGroups = document.getElementById("btn-refresh-groups");

// Join Group Elements
const joinGroupForm = document.getElementById("join-group-form");
const joinInviteCodeInput = document.getElementById("join-invite-code");
const btnJoinGroup = document.getElementById("btn-join-group");

// Group Availability Elements (in Availability Tab)
const groupAvailabilitySection = document.getElementById("group-availability-section");
const availGroupSelect = document.getElementById("avail-group-select");
const groupAvailContent = document.getElementById("group-avail-content");
const groupAvailEmptyState = document.getElementById("group-avail-empty-state");
const groupAvailNoSelection = document.getElementById("group-avail-no-selection");
const availGroupName = document.getElementById("avail-group-name");
const availGroupDesc = document.getElementById("avail-group-desc");
const availGroupRoleBadge = document.getElementById("avail-group-role-badge");
const btnAvailGoToGroups = document.getElementById("btn-avail-go-to-groups");
const btnAvailManageGroup = document.getElementById("btn-avail-manage-group");
const availTabShared = document.getElementById("avail-tab-shared");
const availTabMembers = document.getElementById("avail-tab-members");
const availSharedCountBadge = document.getElementById("avail-shared-count-badge");
const availMembersCount = document.getElementById("avail-members-count");
const availPanelShared = document.getElementById("avail-panel-shared");
const availPanelMembers = document.getElementById("avail-panel-members");
const availMemberFilterChips = document.getElementById("avail-member-filter-chips");
const availBtnSelectAllMembers = document.getElementById("avail-btn-select-all-members");
const availSharedSlotsContainer = document.getElementById("avail-shared-slots-container");
const availMembersList = document.getElementById("avail-members-list");

// Group Details & Management Modal Elements (in Groups Tab)
const groupDetailModal = document.getElementById("group-detail-modal");
const btnCloseGroupModal = document.getElementById("btn-close-group-modal");
const modalGroupName = document.getElementById("modal-group-name");
const modalGroupDesc = document.getElementById("modal-group-desc");
const modalGroupRoleBadge = document.getElementById("modal-group-role-badge");
const modalGroupInviteCode = document.getElementById("modal-group-invite-code");
const btnCopyInviteCode = document.getElementById("btn-copy-invite-code");
const btnCopyInviteLink = document.getElementById("btn-copy-invite-link");
const btnModalViewAvail = document.getElementById("btn-modal-view-avail");
const modalMembersCount = document.getElementById("modal-members-count");
const groupManageMembersList = document.getElementById("group-manage-members-list");
const groupOwnerAddMemberSection = document.getElementById("group-owner-add-member-section");
const addMemberForm = document.getElementById("add-member-form");
const addMemberIdentifier = document.getElementById("add-member-identifier");
const btnAddMember = document.getElementById("btn-add-member");
const modalLeaveGroupSection = document.getElementById("modal-leave-group-section");
const modalDeleteGroupSection = document.getElementById("modal-delete-group-section");
const btnDeleteGroup = document.getElementById("btn-delete-group");
const btnLeaveGroup = document.getElementById("btn-leave-group");

// Edit Profile Elements
const btnToggleEditProfile = document.getElementById("btn-toggle-edit-profile");
const editProfileForm = document.getElementById("edit-profile-form");
const btnCancelEdit = document.getElementById("btn-cancel-edit");
const editFullname = document.getElementById("edit-fullname");
const editUsername = document.getElementById("edit-username");
const editStreet = document.getElementById("edit-street");
const editState = document.getElementById("edit-state");
const editZip = document.getElementById("edit-zip");
const editDistance = document.getElementById("edit-distance");
const btnDeleteAccount = document.getElementById("btn-delete-account");

// Toast Notification Utility
function showToast(message, type = "info", duration = 4000) {
  if (!toastContainer) return;
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

// Auth Tab Switching
function switchTab(target) {
  signupView?.classList.remove("active");
  loginView?.classList.remove("active");
  if (forgotView) forgotView.classList.remove("active");
  if (resetView) resetView.classList.remove("active");
  tabSignupBtn?.classList.remove("active");
  tabSignupBtn?.setAttribute("aria-selected", "false");
  tabLoginBtn?.classList.remove("active");
  tabLoginBtn?.setAttribute("aria-selected", "false");

  if (target === "signup") {
    tabSignupBtn?.classList.add("active");
    tabSignupBtn?.setAttribute("aria-selected", "true");
    signupView?.classList.add("active");
  } else if (target === "login") {
    tabLoginBtn?.classList.add("active");
    tabLoginBtn?.setAttribute("aria-selected", "true");
    loginView?.classList.add("active");
  } else if (target === "forgot") {
    if (forgotView) forgotView.classList.add("active");
  } else if (target === "reset") {
    if (resetView) resetView.classList.add("active");
  }
}

// Dashboard Tab Switching
function switchDashboardTab(targetPanelId) {
  dashTabButtons.forEach((btn) => {
    if (btn.getAttribute("data-target") === targetPanelId) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  dashPanels.forEach((panel) => {
    if (panel.id === targetPanelId) {
      panel.classList.add("active");
    } else {
      panel.classList.remove("active");
    }
  });

  if (targetPanelId === "panel-availability") {
    renderCalendar();
    updateAvailGroupSection();
  }
}

dashTabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const target = btn.getAttribute("data-target");
    if (target) switchDashboardTab(target);
  });
});

if (tabSignupBtn) tabSignupBtn.addEventListener("click", () => switchTab("signup"));
if (tabLoginBtn) tabLoginBtn.addEventListener("click", () => switchTab("login"));
if (linkToLogin) linkToLogin.addEventListener("click", () => switchTab("login"));
if (linkToSignup) linkToSignup.addEventListener("click", () => switchTab("signup"));

if (btnForgotPassword) {
  btnForgotPassword.addEventListener("click", () => {
    const currentId = liIdentifier?.value.trim() || "";
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
      eyeOpen?.classList.add("hidden");
      eyeClosed?.classList.remove("hidden");
    } else {
      input.type = "password";
      eyeOpen?.classList.remove("hidden");
      eyeClosed?.classList.add("hidden");
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

  if (passwordMeterFill) {
    passwordMeterFill.style.width = width;
    passwordMeterFill.style.backgroundColor = color;
  }
  if (passwordStrengthText) {
    passwordStrengthText.textContent = label;
    passwordStrengthText.style.color = color;
  }

  return passedCount === 5;
}

function updateReqItem(element, isMet) {
  if (!element) return;
  const bullet = element.querySelector(".req-bullet");
  if (isMet) {
    element.classList.add("met");
    if (bullet) bullet.textContent = "✓";
  } else {
    element.classList.remove("met");
    if (bullet) bullet.textContent = "•";
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

if (suUsername) suUsername.addEventListener("input", (e) => validateUsername(e.target.value));
if (suEmail) suEmail.addEventListener("input", (e) => validateEmail(e.target.value));
if (suPassword)
  suPassword.addEventListener("input", (e) => {
    evaluatePassword(e.target.value);
    if (suConfirmPassword?.value) checkPasswordMatch();
  });
if (suConfirmPassword) suConfirmPassword.addEventListener("input", checkPasswordMatch);

// Signup Form Submit Handler
if (signupForm) {
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
    if (suTerms && !suTerms.checked) {
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
      if (liIdentifier) liIdentifier.value = username;
      switchTab("login");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setButtonLoading(btnSignup, false);
    }
  });
}

// Login Form Submit Handler
if (loginForm) {
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
}

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

  if (rpPasswordMeterFill) {
    rpPasswordMeterFill.style.width = width;
    rpPasswordMeterFill.style.backgroundColor = color;
  }
  if (rpPasswordStrengthText) {
    rpPasswordStrengthText.textContent = label;
    rpPasswordStrengthText.style.color = color;
  }

  return passedCount === 5;
}

function checkResetPasswordMatch() {
  const pwd = rpPassword.value;
  const confirm = rpConfirmPassword.value;
  if (!confirm) {
    rpConfirmMatchHint.textContent = "";
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
  loadAvailabilities();
  loadUserGroups();

  if (sessionStorage.getItem("pending_join_code")) {
    handlePendingJoinCode();
  } else {
    switchDashboardTab("panel-account");
  }
}

// Dashboard Rendering (Ensures all elements update immediately)
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

  if (dashStreet) {
    dashStreet.textContent = user.street_address ? user.street_address : "Not provided";
  }
  if (dashState) {
    dashState.textContent = user.state ? user.state : "Not provided";
  }
  if (dashZip) {
    dashZip.textContent = user.zip_code ? user.zip_code : "Not provided";
  }
  if (dashDistance) {
    dashDistance.textContent = user.max_travel_distance ? `${user.max_travel_distance} miles` : "Not provided";
  }

  const dateObj = new Date(user.created_at);
  dashJoined.textContent = dateObj.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Logout Handler
btnLogout.addEventListener("click", () => {
  disconnectGroupWebSocket();
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
  if (!button) return;
  const textSpan = button.querySelector(".btn-text");
  const spinner = button.querySelector(".spinner");
  if (isLoading) {
    button.disabled = true;
    textSpan?.classList.add("hidden");
    spinner?.classList.remove("hidden");
  } else {
    button.disabled = false;
    textSpan?.classList.remove("hidden");
    spinner?.classList.add("hidden");
  }
}

// Helper: HTML Escaping
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
  if (!state.token) {
    checkJoinGroupParam();
    return;
  }
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
      loadAvailabilities();
      loadUserGroups();
      if (sessionStorage.getItem("pending_join_code")) {
        handlePendingJoinCode();
      } else {
        switchDashboardTab("panel-account");
      }
      checkJoinGroupParam();
    } else {
      localStorage.removeItem("token");
      state.token = null;
      checkJoinGroupParam();
    }
  } catch (e) {
    checkJoinGroupParam();
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
      const data = await res.json();
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

// ==================== CALENDAR AVAILABILITY ====================
async function loadAvailabilities() {
  if (!state.token) return;
  try {
    const res = await fetch("/api/availability", {
      headers: { Authorization: `Bearer ${state.token}` },
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
  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];
  if (calMonthYear) calMonthYear.textContent = `${monthNames[month]} ${year}`;
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
  calSelectedDateText.textContent = `Slots for ${new Date(y, m - 1, d).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  })}`;

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
      headers: { Authorization: `Bearer ${state.token}` },
    });
    if (!res.ok) throw new Error("Could not delete slot");
    showToast("Availability slot removed", "info");
    await loadAvailabilities();
    if (state.selectedGroup) {
      await loadGroupAvailability(state.selectedGroup.id);
    }
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
          Authorization: `Bearer ${state.token}`,
        },
        body: JSON.stringify({
          date: dateVal,
          start_time: startTime + ":00",
          end_time: endTime + ":00",
          title: titleVal,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to add slot");
      showToast("Slot added!", "success");
      await loadAvailabilities();
      if (state.selectedGroup) {
        await loadGroupAvailability(state.selectedGroup.id);
      }
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
if (btnToggleEditProfile) {
  btnToggleEditProfile.addEventListener("click", () => {
    if (state.currentUser) {
      editFullname.value = state.currentUser.full_name || "";
      editUsername.value = state.currentUser.username || "";
      if (editStreet) editStreet.value = state.currentUser.street_address || "";
      if (editState) editState.value = state.currentUser.state || "";
      if (editZip) editZip.value = state.currentUser.zip_code || "";
      if (editDistance) editDistance.value = state.currentUser.max_travel_distance || "";
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
      const payload = {
        full_name: editFullname.value.trim(),
        username: editUsername.value.trim(),
        street_address: editStreet && editStreet.value.trim() ? editStreet.value.trim() : null,
        state: editState && editState.value.trim() ? editState.value.trim().toUpperCase() : null,
        zip_code: editZip && editZip.value.trim() ? editZip.value.trim() : null,
        max_travel_distance: editDistance && editDistance.value.trim() ? parseInt(editDistance.value.trim(), 10) : null,
      };
      const res = await fetch("/api/users/me", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${state.token}`,
        },
        body: JSON.stringify(payload),
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

// ==================== GROUPS & MEMBERS LOGIC ====================
async function copyToClipboard(text, successMsg) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      const textArea = document.createElement("textarea");
      textArea.value = text;
      textArea.style.position = "fixed";
      textArea.style.left = "-999999px";
      textArea.style.top = "-999999px";
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      document.execCommand("copy");
      textArea.remove();
    }
    showToast(successMsg, "success");
  } catch (err) {
    showToast("Failed to copy to clipboard", "error");
  }
}

function checkJoinGroupParam() {
  const params = new URLSearchParams(window.location.search);
  const joinCode = params.get("join");
  if (!joinCode) return;
  const code = joinCode.trim().toUpperCase();
  if (state.token && state.currentUser) {
    if (joinInviteCodeInput) {
      joinInviteCodeInput.value = code;
    }
    switchDashboardTab("panel-groups");
    showToast(`Invite code ${code} detected. Click 'Join Group' to join.`, "info", 5000);
    window.history.replaceState({}, document.title, window.location.pathname);
  } else {
    sessionStorage.setItem("pending_join_code", code);
    showToast(`Group invite detected (${code})! Please sign in or create an account to join.`, "info", 6000);
    switchTab("login");
  }
}

function handlePendingJoinCode() {
  const pendingCode = sessionStorage.getItem("pending_join_code");
  if (pendingCode) {
    sessionStorage.removeItem("pending_join_code");
    if (joinInviteCodeInput) {
      joinInviteCodeInput.value = pendingCode;
    }
    switchDashboardTab("panel-groups");
    showToast(`Invite code ${pendingCode} ready. Click 'Join Group' to join!`, "info", 6000);
  }
}

async function loadUserGroups() {
  if (!state.token || !groupsListContainer) return;
  try {
    const res = await fetch("/api/groups", {
      headers: { Authorization: `Bearer ${state.token}` },
    });
    if (!res.ok) throw new Error("Failed to load groups");
    const groups = await res.json();
    state.userGroups = groups;
    if (dashGroupsBadge) {
      dashGroupsBadge.textContent = groups.length;
    }
    renderUserGroups();
    updateAvailGroupSection();
  } catch (e) {
    if (groupsListContainer) {
      groupsListContainer.innerHTML = `<p class="cal-empty-slots" style="color: #f87171;">Failed to load groups.</p>`;
    }
  }
}

function renderUserGroups() {
  if (!groupsListContainer) return;
  if (!state.userGroups || state.userGroups.length === 0) {
    groupsListContainer.innerHTML = `<p class="cal-empty-slots">You have not joined or created any groups yet.</p>`;
    return;
  }
  groupsListContainer.innerHTML = state.userGroups
    .map((g) => {
      const isOwner = state.currentUser && g.owner_id === state.currentUser.id;
      return `
        <div class="slot-item group-clickable-card" onclick="openGroupDetail(${g.id})" style="display: flex; align-items: center; gap: 1rem;">
          ${g.group_photo_url ? `<img src="${g.group_photo_url}" style="width: 42px; height: 42px; border-radius: 50%; object-fit: cover; flex-shrink: 0;" />` : ''}
          <div style="flex: 1; min-width: 0;">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
              <strong style="font-size: 0.95rem; color: var(--accent);">${escapeHtml(g.name)}</strong>
              ${g.invite_code ? `<span class="badge" style="background: rgba(255, 255, 255, 0.08); font-family: monospace; font-size: 0.7rem; letter-spacing: 0.5px;">Code: ${escapeHtml(g.invite_code)}</span>` : ""}
            </div>
            ${g.description ? `<p style="color: var(--text-secondary); font-size: 0.78rem; margin: 3px 0 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHtml(g.description)}</p>` : ""}
            <div style="color: var(--text-muted); font-size: 0.72rem; margin-top: 5px;">
              ${g.member_count} member${g.member_count > 1 ? "s" : ""} • Click to view group availability
            </div>
          </div>
          <div style="display: flex; align-items: center; gap: 0.5rem;" onclick="event.stopPropagation()">
            <span class="badge ${isOwner ? "badge-success" : ""}">
              ${isOwner ? "Owner" : "Member"}
            </span>
            <button type="button" class="btn-secondary" onclick="openGroupDetail(${g.id})" style="padding: 0.3rem 0.65rem; font-size: 0.74rem; width: auto; cursor: pointer;" title="Manage members and invite code">
              Manage
            </button>
            <button type="button" class="btn-primary" onclick="openGroupAvailability(${g.id})" style="padding: 0.3rem 0.65rem; font-size: 0.74rem; width: auto; cursor: pointer;" title="View group availability on calendar">
              Availability &rarr;
            </button>
            ${!isOwner ? `
              <button type="button" class="btn-secondary" onclick="leaveGroup(${g.id}, '${escapeHtml(g.name).replace(/'/g, "\\'")}')" style="padding: 0.25rem 0.55rem; font-size: 0.72rem; color: #f87171; border-color: rgba(248, 113, 113, 0.3); cursor: pointer;" title="Leave this group">
                Leave
              </button>
            ` : ""}
          </div>
        </div>
      `;
    })
    .join("");
}

// ==================== TIME & DATE FORMATTING UTILITIES ====================
function formatTime12h(timeStr) {
  if (!timeStr) return "";
  const parts = String(timeStr).split(":");
  let hour = parseInt(parts[0], 10);
  const minute = parts[1] || "00";
  const ampm = hour >= 12 ? "PM" : "AM";
  hour = hour % 12 || 12;
  return `${hour}:${minute} ${ampm}`;
}

function formatDatePretty(dateStr) {
  if (!dateStr) return "";
  const [y, m, d] = dateStr.split("-").map(Number);
  const dateObj = new Date(y, m - 1, d);
  return dateObj.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function timeStrToMinutes(timeStr) {
  const [h, m] = String(timeStr).split(":").map(Number);
  return h * 60 + m;
}

function minutesToTimeStr(mins) {
  const m = Math.max(0, Math.min(mins, 24 * 60 - 1));
  const h = String(Math.floor(m / 60)).padStart(2, "0");
  const min = String(m % 60).padStart(2, "0");
  return `${h}:${min}:00`;
}

function mergeIntervalList(intervals) {
  if (!intervals || intervals.length === 0) return [];
  const sorted = [...intervals].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const merged = [sorted[0]];
  for (let i = 1; i < sorted.length; i++) {
    const prev = merged[merged.length - 1];
    const curr = sorted[i];
    if (curr[0] <= prev[1]) {
      prev[1] = Math.max(prev[1], curr[1]);
    } else {
      merged.push(curr);
    }
  }
  return merged;
}

function computeMutualIntervalsClient(userIntervalsMap, totalMembersCount) {
  if (!userIntervalsMap || totalMembersCount <= 0) {
    return { shared: [], partial: [] };
  }
  const normalized = {};
  const boundariesSet = new Set();
  for (const [userId, intervals] of Object.entries(userIntervalsMap)) {
    const merged = mergeIntervalList(intervals);
    normalized[userId] = merged;
    for (const [start, end] of merged) {
      boundariesSet.add(start);
      boundariesSet.add(end);
    }
  }
  if (boundariesSet.size === 0) return { shared: [], partial: [] };
  const boundaries = Array.from(boundariesSet).sort((a, b) => a - b);
  const rawSegments = [];

  for (let i = 0; i < boundaries.length - 1; i++) {
    const segStart = boundaries[i];
    const segEnd = boundaries[i + 1];
    if (segStart >= segEnd) continue;

    const activeUsers = [];
    for (const [username, intervals] of Object.entries(normalized)) {
      for (const [uStart, uEnd] of intervals) {
        if (uStart <= segStart && segEnd <= uEnd) {
          activeUsers.push(username);
          break;
        }
      }
    }
    if (activeUsers.length > 0) {
      rawSegments.push({
        start: segStart,
        end: segEnd,
        users: activeUsers.sort(),
        count: activeUsers.length,
      });
    }
  }

  function collapseSegments(segs) {
    if (!segs || segs.length === 0) return [];
    const collapsed = [{ ...segs[0] }];
    for (let i = 1; i < segs.length; i++) {
      const prev = collapsed[collapsed.length - 1];
      const curr = segs[i];
      if (prev.end === curr.start && prev.users.join(",") === curr.users.join(",")) {
        prev.end = curr.end;
      } else {
        collapsed.push({ ...curr });
      }
    }
    return collapsed;
  }

  const everyoneSegments = collapseSegments(
    rawSegments.filter((s) => s.count === totalMembersCount)
  );
  const minCount = totalMembersCount > 1 ? 2 : 1;
  const partialSegments = collapseSegments(
    rawSegments.filter((s) => s.count >= minCount && s.count < totalMembersCount)
  );

  return { shared: everyoneSegments, partial: partialSegments };
}

// --- Availability Tab: Sub-Tabs & Filter Logic ---
if (availTabShared && availTabMembers) {
  availTabShared.addEventListener("click", () => {
    availTabShared.classList.add("active");
    availTabMembers.classList.remove("active");
    if (availPanelShared) availPanelShared.classList.remove("hidden");
    if (availPanelMembers) availPanelMembers.classList.add("hidden");
  });
  availTabMembers.addEventListener("click", () => {
    availTabMembers.classList.add("active");
    availTabShared.classList.remove("active");
    if (availPanelMembers) availPanelMembers.classList.remove("hidden");
    if (availPanelShared) availPanelShared.classList.add("hidden");
  });
}

if (availBtnSelectAllMembers) {
  availBtnSelectAllMembers.addEventListener("click", () => {
    if (!state.currentGroupData || !state.currentGroupData.members) return;
    state.selectedMemberIds = new Set(state.currentGroupData.members.map((m) => m.user_id));
    renderMemberFilterChips();
    renderGroupSharedSlots();
  });
}

if (btnAvailManageGroup) {
  btnAvailManageGroup.addEventListener("click", () => {
    if (!state.selectedGroup) return;
    switchDashboardTab("panel-groups");
    openGroupDetail(state.selectedGroup.id);
  });
}

function updateAvailGroupSection() {
  if (!availGroupSelect) return;
  if (!state.userGroups || state.userGroups.length === 0) {
    if (groupAvailEmptyState) groupAvailEmptyState.classList.remove("hidden");
    if (groupAvailNoSelection) groupAvailNoSelection.classList.add("hidden");
    if (groupAvailContent) groupAvailContent.classList.add("hidden");
    availGroupSelect.innerHTML = `<option value="">No groups joined</option>`;
    availGroupSelect.disabled = true;
    return;
  }

  availGroupSelect.disabled = false;
  const currentVal = state.selectedGroup ? state.selectedGroup.id : null;
  availGroupSelect.innerHTML = state.userGroups
    .map((g) => `<option value="${g.id}">${escapeHtml(g.name)} (${g.member_count} member${g.member_count > 1 ? "s" : ""})</option>`)
    .join("");

  if (currentVal && state.userGroups.some((g) => g.id === currentVal)) {
    availGroupSelect.value = String(currentVal);
    selectGroupInAvailability(currentVal, false);
  } else {
    const firstGroup = state.userGroups[0];
    availGroupSelect.value = String(firstGroup.id);
    selectGroupInAvailability(firstGroup.id, false);
  }
}

function selectGroupInAvailability(groupId, shouldScroll = false) {
  const group = state.userGroups.find((g) => g.id === groupId);
  if (!group) return;
  state.selectedGroup = group;
  if (availGroupSelect) availGroupSelect.value = String(groupId);
  if (groupAvailEmptyState) groupAvailEmptyState.classList.add("hidden");
  if (groupAvailNoSelection) groupAvailNoSelection.classList.add("hidden");
  if (groupAvailContent) groupAvailContent.classList.remove("hidden");
  initOrRefreshGroupMap()
  if (availGroupName) availGroupName.textContent = group.name;
  if (availGroupDesc) availGroupDesc.textContent = group.description || "No description provided.";
  const isOwner = state.currentUser && group.owner_id === state.currentUser.id;
  if (availGroupRoleBadge) {
    availGroupRoleBadge.textContent = isOwner ? "Owner" : "Member";
    availGroupRoleBadge.className = isOwner ? "badge badge-success" : "badge";
  }

  if (availTabShared && availTabMembers && availPanelShared && availPanelMembers) {
    if (availPanelShared.classList.contains("hidden") && availPanelMembers.classList.contains("hidden")) {
      availTabShared.classList.add("active");
      availTabMembers.classList.remove("active");
      availPanelShared.classList.remove("hidden");
      availPanelMembers.classList.add("hidden");
    }
  }

  loadGroupAvailability(groupId);
  if (shouldScroll && groupAvailabilitySection) {
    groupAvailabilitySection.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

if (availGroupSelect) {
  availGroupSelect.addEventListener("change", (e) => {
    const groupId = parseInt(e.target.value, 10);
    if (groupId) {
      selectGroupInAvailability(groupId, false);
    } else {
      state.selectedGroup = null;
      if (groupAvailContent) groupAvailContent.classList.add("hidden");
      if (groupAvailNoSelection) groupAvailNoSelection.classList.remove("hidden");
    }
  });
}

if (btnAvailGoToGroups) {
  btnAvailGoToGroups.addEventListener("click", () => {
    switchDashboardTab("panel-groups");
  });
}

window.openGroupAvailability = function (groupId) {
  if (groupDetailModal) groupDetailModal.classList.add("hidden");
  switchDashboardTab("panel-availability");
  selectGroupInAvailability(groupId, true);
};

window.openGroupDetail = async function (groupId) {
  const group = state.userGroups.find((g) => g.id === groupId);
  if (!group) return;
  state.selectedGroup = group;

  if (modalGroupName) modalGroupName.textContent = group.name;
  if (modalGroupDesc) modalGroupDesc.textContent = group.description || "No description provided.";
  if (modalGroupInviteCode) {
    modalGroupInviteCode.textContent = group.invite_code || "--------";
  }
  const isOwner = state.currentUser && group.owner_id === state.currentUser.id;
  if (modalGroupRoleBadge) {
    modalGroupRoleBadge.textContent = isOwner ? "Owner" : "Member";
    modalGroupRoleBadge.className = isOwner ? "badge badge-success" : "badge";
  }

  const groupOwnerAddPollOptionSection = document.getElementById("group-owner-add-poll-option-section");
  if (isOwner) {
    if (groupOwnerAddMemberSection) groupOwnerAddMemberSection.classList.remove("hidden");
    if (groupOwnerAddPollOptionSection) groupOwnerAddPollOptionSection.classList.remove("hidden");
    if (modalLeaveGroupSection) modalLeaveGroupSection.classList.add("hidden");
    if (modalDeleteGroupSection) modalDeleteGroupSection.classList.remove("hidden");
  } else {
    if (groupOwnerAddMemberSection) groupOwnerAddMemberSection.classList.add("hidden");
    if (groupOwnerAddPollOptionSection) groupOwnerAddPollOptionSection.classList.add("hidden");
    if (modalLeaveGroupSection) modalLeaveGroupSection.classList.remove("hidden");
    if (modalDeleteGroupSection) modalDeleteGroupSection.classList.add("hidden");
  }

  if (groupDetailModal) groupDetailModal.classList.remove("hidden");
  await loadGroupMembersForManage(groupId);
  await loadGroupPollOptions(groupId);
};

async function loadGroupMembersForManage(groupId) {
  if (!groupManageMembersList) return;
  groupManageMembersList.innerHTML = `<p class="cal-empty-slots">Loading members...</p>`;
  try {
    const res = await fetch(`/api/groups/${groupId}/availability`, {
      headers: { Authorization: `Bearer ${state.token}` },
    });
    if (!res.ok) throw new Error("Failed to load group members.");
    const data = await res.json();
    if (modalMembersCount) {
      modalMembersCount.textContent = `${data.members.length} member${data.members.length > 1 ? "s" : ""}`;
    }
    const isOwner = state.currentUser && state.selectedGroup && state.selectedGroup.owner_id === state.currentUser.id;
    if (!data.members || data.members.length === 0) {
      groupManageMembersList.innerHTML = `<p class="cal-empty-slots">No members found.</p>`;
      return;
    }
    groupManageMembersList.innerHTML = data.members
      .map((m) => {
        const isMe = state.currentUser && state.currentUser.id === m.user_id;
        const canRemove = isOwner && m.user_id !== state.selectedGroup.owner_id;
        const removeBtn = canRemove
          ? `<button type="button" class="btn-del-slot" onclick="removeMember(${m.user_id})" title="Remove member" style="color: #f87171; font-size: 1.1rem; cursor: pointer;">&times;</button>`
          : "";
        return `
          <div class="member-card" style="margin-bottom: 0.5rem; padding: 0.65rem 0.85rem;">
            <div class="member-card-header" style="margin-bottom: 0;">
              <div>
                <strong style="color: var(--text-main); font-size: 0.88rem;">
                  ${escapeHtml(m.full_name || "No name provided")} ${isMe ? "(You)" : ""}
                </strong>
                <span style="color: var(--accent); font-size: 0.78rem; margin-left: 0.35rem;">
                  @${escapeHtml(m.username)}
                </span>
              </div>
              <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span class="badge ${m.role === "owner" ? "badge-success" : ""}">${m.role}</span>
                ${removeBtn}
              </div>
            </div>
          </div>
        `;
      })
      .join("");
  } catch (err) {
    groupManageMembersList.innerHTML = `<p class="cal-empty-slots" style="color: #f87171;">${err.message}</p>`;
  }
}

async function loadGroupPollOptions(groupId) {
  const container = document.getElementById("group-poll-options-list");
  if (!container) return;
  container.innerHTML = `<span style="font-size: 0.75rem; color: var(--text-muted);">Loading options...</span>`;
  try {
    const res = await fetch(`/api/groups/${groupId}/poll-options`, {
      headers: { Authorization: `Bearer ${state.token}` },
    });
    if (!res.ok) throw new Error("Failed to load group poll options.");
    const options = await res.json();
    state.currentGroupPollOptions = options;
    const isOwner = Boolean(
      state.currentUser &&
      state.selectedGroup &&
      state.selectedGroup.owner_id === state.currentUser.id
    );
    if (!options || options.length === 0) {
      container.innerHTML = `<span style="font-size: 0.75rem; color: var(--text-muted);">No options configured.</span>`;
      return;
    }
    container.innerHTML = options
      .map((opt) => {
        const isDefault = opt.is_default;
        const deleteBtn = isOwner && !isDefault
          ? `<button type="button" class="btn-del-group-opt" onclick="deleteGroupPollOption(${groupId}, ${opt.id})" title="Remove option from all polls">&times;</button>`
          : "";
        return `
          <span class="group-opt-chip ${isDefault ? 'default-opt' : ''}">
            <span>${escapeHtml(opt.text)}</span>
            ${isDefault ? '<small style="font-size: 0.68rem; color: var(--text-muted);">(Default)</small>' : ''}
            ${deleteBtn}
          </span>
        `;
      })
      .join("");
  } catch (err) {
    container.innerHTML = `<span style="font-size: 0.75rem; color: #f87171;">${escapeHtml(err.message)}</span>`;
  }
}

window.deleteGroupPollOption = async function (groupId, optionId) {
  if (!confirm("Remove this option from all current and future group polls?")) {
    return;
  }
  try {
    const res = await fetch(`/api/groups/${groupId}/poll-options/${optionId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${state.token}` },
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to remove option.");
    }
    const updatedOptions = await res.json();
    state.currentGroupPollOptions = updatedOptions;
    await loadGroupPollOptions(groupId);
    showToast("Poll option removed from all polls.", "info");
    if (state.selectedGroup && state.selectedGroup.id === groupId) {
      await loadGroupAvailability(groupId);
    }
  } catch (err) {
    showToast(err.message, "error");
  }
};

// ==================== REAL-TIME HANGOUT POLLS & VOTING ====================
let groupWebSocket = null;

function connectGroupWebSocket(groupId) {
  if (!groupId || !state.token) return;
  if (groupWebSocket) {
    try {
      groupWebSocket.close();
    } catch (_) {}
    groupWebSocket = null;
  }

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/groups/${groupId}?token=${encodeURIComponent(state.token)}`;

  try {
    groupWebSocket = new WebSocket(wsUrl);
    groupWebSocket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "POLL_UPDATED" && msg.poll) {
          updatePollCardDOM(msg.poll);
        } else if (msg.type === "POLL_DELETED" && msg.poll_id) {
          delete state.currentGroupPolls[msg.poll_id];
          if (msg.date && msg.start_time && msg.end_time) {
            const key = `${msg.date}_${String(msg.start_time).slice(0, 5)}_${String(msg.end_time).slice(0, 5)}`;
            delete state.currentGroupPolls[key];
          }
          const pollSection = document.getElementById(`poll-section-${msg.poll_id}`);
          if (pollSection) pollSection.remove();
          renderGroupSharedSlots();
          showToast("A hangout poll was removed.", "info");
        } else if (msg.type === "GROUP_OPTIONS_UPDATED") {
          if (state.selectedGroup && state.selectedGroup.id === msg.group_id) {
            loadGroupPollOptions(msg.group_id);
            loadGroupAvailability(msg.group_id);
          }
        }
      } catch (err) {
        console.warn("WebSocket parse error:", err);
      }
    };
    groupWebSocket.onclose = () => {
      groupWebSocket = null;
    };
    groupWebSocket.onerror = (err) => {
      console.warn("WebSocket error:", err);
    };
  } catch (e) {
    console.warn("Failed to initiate WebSocket:", e);
  }
}

function disconnectGroupWebSocket() {
  if (groupWebSocket) {
    try {
      groupWebSocket.close();
    } catch (_) {}
    groupWebSocket = null;
  }
}

function renderPollHtml(poll, isLeader, groupId) {
  if (!poll || poll.is_deleted) return "";
  
  // Filter poll options so the poll card ONLY displays Yes, No, and custom poll options added by the group leader
  const groupCustomTexts = new Set(
    (state.currentGroupPollOptions || []).map((o) => o.text.trim().toLowerCase())
  );
  const visibleOptions = (poll.options || []).filter((opt) => {
    const textLower = opt.text.trim().toLowerCase();
    return textLower === "yes" || textLower === "no" || groupCustomTexts.has(textLower);
  });

  const totalVotes = visibleOptions.reduce((acc, opt) => acc + (opt.count || 0), 0);

  const progressBars = visibleOptions.map((opt) => {
    let color = "#6366f1";
    if (opt.text.toLowerCase() === "yes") color = "#10b981";
    else if (opt.text.toLowerCase() === "no") color = "#ef4444";
    const pct = totalVotes > 0 ? Math.round((opt.count / totalVotes) * 1000) / 10 : 0;
    return `<div class="poll-progress-segment" style="width: ${pct}%; background: ${color};" title="${escapeHtml(opt.text)}: ${opt.count} (${pct}%)"></div>`;
  }).join("");

  const optionsHtml = visibleOptions.map((opt) => {
    const isVoted = poll.my_vote_option_id === opt.id;
    const textLower = opt.text.toLowerCase();
    const pct = totalVotes > 0 ? Math.round((opt.count / totalVotes) * 1000) / 10 : 0;
    let optClass = "poll-option-btn";
    if (textLower === "yes") optClass += " opt-yes";
    if (textLower === "no") optClass += " opt-no";
    if (isVoted) optClass += " active";
    return `
      <button type="button" class="${optClass}" onclick="castHangoutVote(${groupId}, ${poll.id}, ${opt.id})" title="${opt.voters && opt.voters.length ? `Voters: @${opt.voters.join(', @')}` : 'No votes yet'}">
        <span>${textLower === "yes" ? "👍 " : (textLower === "no" ? "👎 " : "")}${escapeHtml(opt.text)}</span>
        <span class="poll-stat-badge">${opt.count} (${pct}%)</span>
      </button>
    `;
  }).join("");

  const deletePollBtn = isLeader
    ? `<button type="button" class="btn-del-poll" onclick="deleteHangoutPoll(${groupId}, ${poll.id}, '${poll.date}', '${poll.start_time}', '${poll.end_time}')" title="Delete Poll">Delete Poll</button>`
    : "";

  // Determine Current Place:
  // Derived from user votes on places in the "Find Activities & Food" menu.
  // Falls back to "Not Yet Decided" if no votes yet.
  let currentPlaceText = poll.current_place || "Not Yet Decided";
  if (poll.place_votes && poll.place_votes.length > 0) {
    let maxVotes = 0;
    for (const pv of poll.place_votes) {
      if (pv.count > maxVotes) maxVotes = pv.count;
    }
    if (maxVotes > 0) {
      const topPlaces = poll.place_votes.filter((pv) => pv.count === maxVotes);
      currentPlaceText = topPlaces.map((tp) => tp.place_name).join(" / ");
    } else {
      currentPlaceText = "Not Yet Decided";
    }
  }

  const recBtnHtml = `
    <button type="button" class="btn-rec-trigger" onclick="openRecommendationsModal(${poll.id}, ${groupId || (state.selectedGroup ? state.selectedGroup.id : null)})" title="Explore open restaurants, activities, and events tailored to group commute">
      🔍 Find Activities & Food
    </button>
  `;

  return `
    <div class="hangout-place-display">
      <span class="hangout-place-label">📍 Current Place:</span>
      <span class="hangout-place-value">${escapeHtml(currentPlaceText)}</span>
    </div>
    <div class="poll-section" id="poll-section-${poll.id}">
      <div class="poll-header">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span style="font-size: 0.74rem;">${totalVotes} vote${totalVotes === 1 ? "" : "s"} total</span>
          ${deletePollBtn}
        </div>
      </div>
      <div class="poll-progress-container">
        ${totalVotes > 0 ? progressBars : `<div class="poll-progress-segment" style="width: 100%; background: rgba(255,255,255,0.06);"></div>`}
      </div>
      <div class="poll-options-row">
        <div class="poll-options-list">
          ${optionsHtml}
        </div>
        ${recBtnHtml}
      </div>
    </div>
  `;
}

function updatePollCardDOM(poll) {
  if (!poll || poll.is_deleted) return;
  state.currentGroupPolls[poll.id] = poll;
  const pollKey = `${poll.date}_${String(poll.start_time).slice(0, 5)}_${String(poll.end_time).slice(0, 5)}`;
  state.currentGroupPolls[pollKey] = poll;

  const pollWrapper = document.getElementById(`slot-poll-wrapper-${poll.id}`);
  if (pollWrapper) {
    const isLeader = Boolean(
      state.selectedGroup &&
      state.currentUser &&
      state.selectedGroup.owner_id === state.currentUser.id
    );
    pollWrapper.innerHTML = renderPollHtml(poll, isLeader, poll.group_id);
    return;
  }

  // Fallback to legacy poll-section selector if wrapper not found
  const pollSection = document.getElementById(`poll-section-${poll.id}`);
  if (pollSection) {
    const isLeader = Boolean(
      state.selectedGroup &&
      state.currentUser &&
      state.selectedGroup.owner_id === state.currentUser.id
    );
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = renderPollHtml(poll, isLeader, poll.group_id);
    const newSection = tempDiv.querySelector(".poll-section");
    if (newSection) {
      pollSection.replaceWith(newSection);
    }
  }
}

window.deleteHangoutPoll = async function (groupId, pollId, pDate, pStart, pEnd) {
  if (!confirm("Are you sure you want to delete this poll? All recorded votes will be removed.")) {
    return;
  }
  try {
    const res = await fetch(`/api/groups/${groupId}/hangouts/${pollId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${state.token}` },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to delete poll.");
    showToast("Poll deleted successfully.", "info");

    delete state.currentGroupPolls[pollId];

    if (pDate && pStart && pEnd) {
      const key5 = `${pDate}_${String(pStart).slice(0, 5)}_${String(pEnd).slice(0, 5)}`;
      delete state.currentGroupPolls[key5];
    }

    const pollSection = document.getElementById(`poll-section-${pollId}`);
    if (pollSection) pollSection.remove();
    renderGroupSharedSlots();
  } catch (err) {
    showToast(err.message, "error");
  }
};

window.castHangoutVote = async function (groupId, pollId, optionId) {
  if (!state.token) return;
  try {
    const res = await fetch(`/api/groups/${groupId}/hangouts/${pollId}/vote`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${state.token}`,
      },
      body: JSON.stringify({ option_id: optionId }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to submit vote.");
    }
    const updatedPoll = await res.json();
    updatePollCardDOM(updatedPoll);
  } catch (err) {
    showToast(err.message, "error");
  }
};

const groupAddPollOptionForm = document.getElementById("group-add-poll-option-form");
const groupPollOptionInput = document.getElementById("group-poll-option-input");

if (groupAddPollOptionForm) {
  groupAddPollOptionForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!state.selectedGroup || !groupPollOptionInput) return;
    const text = groupPollOptionInput.value.trim();
    if (!text) {
      showToast("Please enter an option name.", "info");
      return;
    }
    const btn = document.getElementById("btn-group-add-poll-option");
    const btnText = btn ? btn.querySelector(".btn-text") : null;
    const spinner = btn ? btn.querySelector(".spinner") : null;
    if (btnText) btnText.classList.add("hidden");
    if (spinner) spinner.classList.remove("hidden");
    if (btn) btn.disabled = true;

    try {
      const res = await fetch(`/api/groups/${state.selectedGroup.id}/poll-options`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${state.token}`,
        },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to add option.");
      }
      const updatedOptions = await res.json();
      state.currentGroupPollOptions = updatedOptions;
      groupPollOptionInput.value = "";
      await loadGroupPollOptions(state.selectedGroup.id);
      showToast(`Added option "${text}" to all current and future polls!`, "success");
      if (state.selectedGroup) {
        await loadGroupAvailability(state.selectedGroup.id);
      }
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      if (btnText) btnText.classList.remove("hidden");
      if (spinner) spinner.classList.add("hidden");
      if (btn) btn.disabled = false;
    }
  });
}

async function loadGroupAvailability(groupId) {
  if (!availSharedSlotsContainer || !availMembersList) return;
  availSharedSlotsContainer.innerHTML = `<p class="cal-empty-slots">Loading group availability...</p>`;
  availMembersList.innerHTML = `<p class="cal-empty-slots">Loading member schedules...</p>`;
  try {
    connectGroupWebSocket(groupId);
    const res = await fetch(`/api/groups/${groupId}/availability`, {
      headers: { Authorization: `Bearer ${state.token}` },
    });
    if (!res.ok) throw new Error("Failed to load group availability.");
    const data = await res.json();
    state.currentGroupData = data;
    state.currentGroupPolls = {};
    if (data.polls && Array.isArray(data.polls)) {
      data.polls.forEach((p) => {
        state.currentGroupPolls[p.id] = p;
        const key = `${p.date}_${String(p.start_time).slice(0, 5)}_${String(p.end_time).slice(0, 5)}`;
        state.currentGroupPolls[key] = p;
      });
    }
    state.selectedMemberIds = new Set(data.members.map((m) => m.user_id));
    if (availMembersCount) {
      availMembersCount.textContent = `${data.members.length} member${data.members.length > 1 ? "s" : ""}`;
    }
    renderMemberFilterChips();
    renderGroupSharedSlots();
    renderGroupIndividualMembers(data.members);
  } catch (err) {
    if (availSharedSlotsContainer) availSharedSlotsContainer.innerHTML = `<p class="cal-empty-slots" style="color: #f87171;">${err.message}</p>`;
    if (availMembersList) availMembersList.innerHTML = `<p class="cal-empty-slots" style="color: #f87171;">${err.message}</p>`;
  }
}

function renderMemberFilterChips() {
  if (!availMemberFilterChips || !state.currentGroupData) return;
  const members = state.currentGroupData.members || [];
  availMemberFilterChips.innerHTML = members
    .map((m) => {
      const isSelected = state.selectedMemberIds.has(m.user_id);
      const isMe = state.currentUser && state.currentUser.id === m.user_id;
      const label = isMe ? "You" : (m.full_name || `@${m.username}`);
      return `
        <span class="member-chip ${isSelected ? "selected" : ""}" onclick="toggleGroupMemberFilter(${m.user_id})">
          <input type="checkbox" ${isSelected ? "checked" : ""} style="pointer-events: none; accent-color: var(--primary);" />
          <span>${escapeHtml(label)}</span>
        </span>
      `;
    })
    .join("");
}

window.toggleGroupMemberFilter = function (userId) {
  if (!state.selectedMemberIds) return;
  if (state.selectedMemberIds.has(userId)) {
    if (state.selectedMemberIds.size <= 1) {
      showToast("At least one member must remain selected.", "info");
      return;
    }
    state.selectedMemberIds.delete(userId);
  } else {
    state.selectedMemberIds.add(userId);
  }
  renderMemberFilterChips();
  renderGroupSharedSlots();
};

function renderGroupSharedSlots() {
  if (!availSharedSlotsContainer || !state.currentGroupData) return;
  const allMembers = state.currentGroupData.members || [];
  const selectedMembers = allMembers.filter((m) => state.selectedMemberIds.has(m.user_id));
  const totalSelected = selectedMembers.length;

  if (totalSelected === 0) {
    availSharedSlotsContainer.innerHTML = `<p class="cal-empty-slots">Please select at least one member to calculate shared times.</p>`;
    if (availSharedCountBadge) availSharedCountBadge.textContent = "0";
    return;
  }

  const datesMap = {};
  selectedMembers.forEach((m) => {
    (m.availabilities || []).forEach((slot) => {
      if (!datesMap[slot.date]) datesMap[slot.date] = {};
      if (!datesMap[slot.date][m.username]) datesMap[slot.date][m.username] = [];
      datesMap[slot.date][m.username].push([
        timeStrToMinutes(slot.start_time),
        timeStrToMinutes(slot.end_time),
      ]);
    });
  });

  const sortedDates = Object.keys(datesMap).sort();
  const allSharedList = [];
  const allPartialList = [];

  sortedDates.forEach((d) => {
    const userIntervals = datesMap[d];
    const { shared, partial } = computeMutualIntervalsClient(userIntervals, totalSelected);
    shared.forEach((s) => {
      allSharedList.push({
        date: d,
        start_time: minutesToTimeStr(s.start),
        end_time: minutesToTimeStr(s.end),
        users: s.users,
        count: s.count,
        total: totalSelected,
        is_everyone: true,
      });
    });
    partial.forEach((p) => {
      allPartialList.push({
        date: d,
        start_time: minutesToTimeStr(p.start),
        end_time: minutesToTimeStr(p.end),
        users: p.users,
        count: p.count,
        total: totalSelected,
        is_everyone: false,
      });
    });
  });

  if (availSharedCountBadge) {
    availSharedCountBadge.textContent = String(allSharedList.length);
  }

  if (allSharedList.length === 0 && allPartialList.length === 0) {
    availSharedSlotsContainer.innerHTML = `
      <div style="text-align: center; padding: 1.5rem 1rem;">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🗓</div>
        <p style="color: var(--text-main); font-weight: 600; margin-bottom: 0.35rem;">No overlapping free times found</p>
        <p style="color: var(--text-muted); font-size: 0.8rem; margin: 0;">
          The selected ${totalSelected} member${totalSelected > 1 ? "s" : ""} have no overlapping hours. Try unchecking busy members or ask members to add more open slots.
        </p>
      </div>
    `;
    return;
  }

  let html = "";
  if (allSharedList.length > 0) {
    html += `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
        <span style="font-size: 0.78rem; font-weight: 700; color: #34d399; text-transform: uppercase; letter-spacing: 0.04em;">
          Times When All ${totalSelected} Selected Members Are Free (${allSharedList.length})
        </span>
      </div>
    `;
    html += allSharedList
      .map((slot) => {
        const startTime12 = formatTime12h(slot.start_time);
        const endTime12 = formatTime12h(slot.end_time);
        const dateFormatted = formatDatePretty(slot.date);
        const userTags = slot.users
          .map((u) => `<span class="avail-pill" style="background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.3); color: #34d399;">@${escapeHtml(u)}</span>`)
          .join("");
        const pollKey = `${slot.date}_${String(slot.start_time).slice(0, 5)}_${String(slot.end_time).slice(0, 5)}`;
        const poll = (state.currentGroupPolls && state.currentGroupPolls[pollKey]) || null;
        const isLeader = Boolean(
          state.selectedGroup &&
          state.currentUser &&
          state.selectedGroup.owner_id === state.currentUser.id
        );
        const pollHtml = renderPollHtml(poll, isLeader, state.selectedGroup ? state.selectedGroup.id : null);
        return `
          <div class="shared-slot-card">
            <div class="shared-slot-header">
              <span class="shared-slot-datetime">
                <span>🗓️ ${escapeHtml(dateFormatted)}</span>
                <span class="slot-datetime-sep">•</span>
                <span>${startTime12} – ${endTime12}</span>
              </span>
              <span class="badge-everyone">All ${slot.total} Free</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; margin-top: 0.35rem;">
              <span style="font-size: 0.72rem; color: var(--text-secondary);">Available:</span>
              ${userTags}
            </div>
            <div id="${poll ? `slot-poll-wrapper-${poll.id}` : ''}">
              ${pollHtml}
            </div>
          </div>
        `;
      })
      .join("");
  }

  if (allPartialList.length > 0 && totalSelected > 2) {
    html += `
      <div style="margin-top: 1.25rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 0.78rem; font-weight: 700; color: #fbbf24; text-transform: uppercase; letter-spacing: 0.04em;">
          Partial Overlaps (${allPartialList.length})
        </span>
      </div>
    `;
    html += allPartialList
      .map((slot) => {
        const startTime12 = formatTime12h(slot.start_time);
        const endTime12 = formatTime12h(slot.end_time);
        const dateFormatted = formatDatePretty(slot.date);
        const userTags = slot.users
          .map((u) => `<span class="avail-pill" style="background: rgba(245, 158, 11, 0.15); border-color: rgba(245, 158, 11, 0.3); color: #fbbf24;">@${escapeHtml(u)}</span>`)
          .join("");
        const pollKey = `${slot.date}_${String(slot.start_time).slice(0, 5)}_${String(slot.end_time).slice(0, 5)}`;
        const poll = (state.currentGroupPolls && state.currentGroupPolls[pollKey]) || null;
        const isLeader = Boolean(
          state.selectedGroup &&
          state.currentUser &&
          state.selectedGroup.owner_id === state.currentUser.id
        );
        const pollHtml = renderPollHtml(poll, isLeader, state.selectedGroup ? state.selectedGroup.id : null);
        return `
          <div class="shared-slot-card partial">
            <div class="shared-slot-header">
              <span class="shared-slot-datetime">
                <span>🗓️ ${escapeHtml(dateFormatted)}</span>
                <span class="slot-datetime-sep">•</span>
                <span>${startTime12} – ${endTime12}</span>
              </span>
              <span class="badge-partial">${slot.count} of ${slot.total} Free</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; margin-top: 0.35rem;">
              <span style="font-size: 0.72rem; color: var(--text-secondary);">Available:</span>
              ${userTags}
            </div>
            <div id="${poll ? `slot-poll-wrapper-${poll.id}` : ''}">
              ${pollHtml}
            </div>
          </div>
        `;
      })
      .join("");
  }
  availSharedSlotsContainer.innerHTML = html;
}

function renderGroupIndividualMembers(members) {
  if (!availMembersList) return;
  if (!members || members.length === 0) {
    availMembersList.innerHTML = `<p class="cal-empty-slots">No members found in this group.</p>`;
    return;
  }
  availMembersList.innerHTML = members
    .map((m) => {
      let availHtml = "";
      if (m.availabilities && m.availabilities.length > 0) {
        availHtml = `
          <div class="member-avail-pills">
            ${m.availabilities
              .map((a) => {
                const s12 = formatTime12h(a.start_time);
                const e12 = formatTime12h(a.end_time);
                const datePretty = formatDatePretty(a.date);
                return `
                  <span class="avail-pill" title="${escapeHtml(a.title || 'Available')}">
                    <strong>${escapeHtml(datePretty)}</strong>: ${s12} – ${e12} <span style="opacity: 0.7;">(${escapeHtml(a.title || 'Available')})</span>
                  </span>
                `;
              })
              .join("")}
          </div>
        `;
      } else {
        availHtml = `<div style="font-size: 0.74rem; color: var(--text-muted); margin-top: 4px; font-style: italic;">No availability registered yet.</div>`;
      }
      return `
        <div class="member-card">
          <div class="member-card-header">
            <div>
              <strong style="color: var(--text-main); font-size: 0.9rem;">
                ${escapeHtml(m.full_name || "No name provided")}
              </strong>
              <span style="color: var(--accent); font-size: 0.8rem; margin-left: 0.35rem;">
                @${escapeHtml(m.username)}
              </span>
            </div>
            <div>
              <span class="badge ${m.role === "owner" ? "badge-success" : ""}">${m.role}</span>
            </div>
          </div>
          ${availHtml}
        </div>
      `;
    })
    .join("");
}

// Remove member logic (Owner only, in Groups Tab)
window.removeMember = async function (userId) {
  if (!state.selectedGroup) return;
  const confirmed = confirm("Are you sure you want to remove this member from the group?");
  if (!confirmed) return;
  try {
    const res = await fetch(`/api/groups/${state.selectedGroup.id}/members/${userId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${state.token}` },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to remove member.");
    showToast(data.message || "Member removed.", "info");
    await loadGroupMembersForManage(state.selectedGroup.id);
    await loadGroupAvailability(state.selectedGroup.id);
    await loadUserGroups();
  } catch (err) {
    showToast(err.message, "error");
  }
};

// Leave group logic (Non-owner members, in Groups Tab)
window.leaveGroup = async function (groupId, groupName) {
  const name = groupName || "this group";
  if (!confirm(`Are you sure you want to leave "${name}"?`)) {
    return;
  }
  try {
    const res = await fetch(`/api/groups/${groupId}/leave`, {
      method: "POST",
      headers: { Authorization: `Bearer ${state.token}` },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to leave group.");
    showToast(data.message || `Left "${name}" successfully.`, "info");
    if (state.selectedGroup && state.selectedGroup.id === groupId) {
      if (groupDetailModal) groupDetailModal.classList.add("hidden");
      state.selectedGroup = null;
    }
    await loadUserGroups();
  } catch (err) {
    showToast(err.message, "error");
  }
};

// Add member logic (Owner only, in Groups Tab)
if (addMemberForm) {
  addMemberForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!state.selectedGroup) return;
    const identifier = addMemberIdentifier.value.trim();
    if (!identifier) return;
    setButtonLoading(btnAddMember, true);
    try {
      const res = await fetch(`/api/groups/${state.selectedGroup.id}/members`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${state.token}`,
        },
        body: JSON.stringify({ identifier }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to add member.");
      showToast(data.message || "Member added!", "success");
      addMemberIdentifier.value = "";
      await loadGroupMembersForManage(state.selectedGroup.id);
      await loadGroupAvailability(state.selectedGroup.id);
      await loadUserGroups();
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setButtonLoading(btnAddMember, false);
    }
  });
}

// Copy Invite Code and Link (in Groups Tab Modal)
if (btnCopyInviteCode) {
  btnCopyInviteCode.addEventListener("click", () => {
    if (!state.selectedGroup || !state.selectedGroup.invite_code) return;
    copyToClipboard(state.selectedGroup.invite_code, "Invite code copied to clipboard!");
  });
}

if (btnCopyInviteLink) {
  btnCopyInviteLink.addEventListener("click", () => {
    if (!state.selectedGroup || !state.selectedGroup.invite_code) return;
    const inviteUrl = `${window.location.origin}/?join=${encodeURIComponent(state.selectedGroup.invite_code)}`;
    copyToClipboard(inviteUrl, "Invite link copied to clipboard!");
  });
}

// View Availability CTA inside modal
if (btnModalViewAvail) {
  btnModalViewAvail.addEventListener("click", () => {
    if (!state.selectedGroup) return;
    openGroupAvailability(state.selectedGroup.id);
  });
}

// Leave group button inside modal
if (btnLeaveGroup) {
  btnLeaveGroup.addEventListener("click", async () => {
    if (!state.selectedGroup) return;
    await leaveGroup(state.selectedGroup.id, state.selectedGroup.name);
  });
}

// Delete group logic (Owner only, in Groups Tab)
window.deleteGroup = async function (groupId, groupName) {
  const name = groupName || "this group";
  const confirmed = confirm(`Are you sure you want to permanently delete "${name}"? This action cannot be undone and will remove all group memberships.`);
  if (!confirmed) return;
  try {
    const res = await fetch(`/api/groups/${groupId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${state.token}` },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to delete group.");
    showToast(data.message || `Deleted "${name}" successfully.`, "info");
    
    if (groupDetailModal) groupDetailModal.classList.add("hidden");
    if (state.selectedGroup && state.selectedGroup.id === groupId) {
      state.selectedGroup = null;
    }
    await loadUserGroups();
  } catch (err) {
    showToast(err.message, "error");
  }
};

if (btnDeleteGroup) {
  btnDeleteGroup.addEventListener("click", async () => {
    if (!state.selectedGroup) return;
    await deleteGroup(state.selectedGroup.id, state.selectedGroup.name);
  });
}

// Close Modal
if (btnCloseGroupModal) {
  btnCloseGroupModal.addEventListener("click", () => {
    if (groupDetailModal) groupDetailModal.classList.add("hidden");
  });
}

if (btnRefreshGroups) {
  btnRefreshGroups.addEventListener("click", loadUserGroups);
}

// Create Group Form
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

      const photoInput = document.getElementById("group-photo-input");
      if (response.ok && photoInput && photoInput.files[0]) {
        const formData = new FormData();
        formData.append("file", photoInput.files[0]);
        await fetch(`/api/groups/${data.id}/photo`, {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${state.token}`,
          },
          body: formData,
        });
      }
      if (!response.ok) {
        throw new Error(data.detail || "Failed to create group.");
      }
      showToast(`Group "${data.name}" created successfully! Invite code: ${data.invite_code}`, "success", 6000);
      createGroupForm.reset();
      await loadUserGroups();
      switchDashboardTab("panel-groups");
      openGroupDetail(data.id);
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setButtonLoading(btnCreateGroup, false);
    }
  });
}

// Join Group Form
if (joinGroupForm) {
  joinGroupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const code = joinInviteCodeInput ? joinInviteCodeInput.value.trim().toUpperCase() : "";
    if (!code) {
      showToast("Please enter an invite code.", "error");
      if (joinInviteCodeInput) joinInviteCodeInput.focus();
      return;
    }
    setButtonLoading(btnJoinGroup, true);
    try {
      const response = await fetch("/api/groups/join", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${state.token}`,
        },
        body: JSON.stringify({ invite_code: code }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to join group.");
      }
      showToast(`Successfully joined group "${data.name}"!`, "success", 5000);
      joinGroupForm.reset();
      await loadUserGroups();
      switchDashboardTab("panel-groups");
      openGroupDetail(data.group_id);
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setButtonLoading(btnJoinGroup, false);
    }
  });
}

// --- Recommendations & Activity Finder Modal Logic ---
const recommendationsModal = document.getElementById("recommendations-modal");
const btnCloseRecModal = document.getElementById("btn-close-rec-modal");
const recModalSlotInfo = document.getElementById("rec-modal-slot-info");
const recMidpointText = document.getElementById("rec-midpoint-text");
const recMissingAddressWarning = document.getElementById("rec-missing-address-warning");
const recMissingUsersList = document.getElementById("rec-missing-users-list");
const recTabFood = document.getElementById("rec-tab-food");
const recTabEntertainment = document.getElementById("rec-tab-entertainment");
const recItemsCount = document.getElementById("rec-items-count");
const recLoadingSpinner = document.getElementById("rec-loading-spinner");
const recCardsList = document.getElementById("rec-cards-list");
const recSourceNotice = document.getElementById("rec-source-notice");
const recSourceIcon = document.getElementById("rec-source-icon");
const recSourceText = document.getElementById("rec-source-text");
const recBudgetPills = document.getElementById("rec-budget-pills");
const recDistanceFilter = document.getElementById("rec-distance-filter");
const recWithinLimitsCheck = document.getElementById("rec-within-limits-check");
const recSortFilter = document.getElementById("rec-sort-filter");

state.activeRecPoll = null;
state.activeRecCategory = "food";
state.recCache = {};
state.recFilters = {
  budget: "all",
  maxDistance: null,
  withinLimitsOnly: false,
  sortBy: "recommended",
};

window.setRecBudgetFilter = function (budgetVal, btnEl) {
  state.recFilters.budget = budgetVal;
  if (recBudgetPills) {
    recBudgetPills.querySelectorAll(".rec-pill-btn").forEach((btn) => btn.classList.remove("active"));
  }
  if (btnEl) btnEl.classList.add("active");
  applyRecFilters();
};

window.applyRecFilterChange = function () {
  if (recDistanceFilter) {
    const val = recDistanceFilter.value.trim();
    state.recFilters.maxDistance = val ? parseFloat(val) : null;
  }
  if (recWithinLimitsCheck) {
    state.recFilters.withinLimitsOnly = Boolean(recWithinLimitsCheck.checked);
  }
  if (recSortFilter) {
    state.recFilters.sortBy = recSortFilter.value.trim() || "recommended";
  }
  applyRecFilters();
};

function applyRecFilters() {
  if (!state.activeRecPoll) return;
  const { pollId } = state.activeRecPoll;
  const category = state.activeRecCategory || "food";
  const cacheKey = `${pollId}_${category}`;
  const data = state.recCache[cacheKey];
  if (data) {
    renderRecommendationsList(data);
  } else {
    loadPollRecommendations(category);
  }
}

window.openRecommendationsModal = async function (pollId, groupId, dateStr, startTime, endTime, currentPlace) {
  try {
    const effectiveGroupId = groupId || (state.selectedGroup ? state.selectedGroup.id : null);
    const poll = (state.currentGroupPolls && state.currentGroupPolls[pollId]) || null;
    const effectiveDate = dateStr || (poll ? poll.date : "");
    const effectiveStart = startTime || (poll ? poll.start_time : "");
    const effectiveEnd = endTime || (poll ? poll.end_time : "");
    const effectivePlace = currentPlace || (poll ? poll.place : "");

    state.activeRecPoll = {
      pollId,
      groupId: effectiveGroupId,
      dateStr: effectiveDate,
      startTime: effectiveStart,
      endTime: effectiveEnd,
      currentPlace: effectivePlace,
    };
    state.activeRecCategory = "food";

    if (recModalSlotInfo) {
      const formattedDate = effectiveDate ? formatDatePretty(effectiveDate) : "";
      const startFmt = effectiveStart ? formatTime12h(String(effectiveStart).slice(0, 5)) : "";
      const endFmt = effectiveEnd ? formatTime12h(String(effectiveEnd).slice(0, 5)) : "";
      recModalSlotInfo.textContent = formattedDate ? `📅 ${formattedDate} • ${startFmt} – ${endFmt}` : "Hangout Slot";
    }

    if (recTabFood) recTabFood.classList.add("active");
    if (recTabEntertainment) recTabEntertainment.classList.remove("active");

    if (recommendationsModal) recommendationsModal.classList.remove("hidden");
    await loadPollRecommendations("food");
  } catch (err) {
    console.error("Error opening recommendations modal:", err);
    if (recommendationsModal) recommendationsModal.classList.remove("hidden");
    showToast("Failed to initialize recommendations: " + err.message, "error");
  }
};

window.closeRecommendationsModal = function () {
  if (recommendationsModal) recommendationsModal.classList.add("hidden");
  state.activeRecPoll = null;
};

if (btnCloseRecModal) {
  btnCloseRecModal.addEventListener("click", closeRecommendationsModal);
}
if (recommendationsModal) {
  recommendationsModal.addEventListener("click", (e) => {
    if (e.target === recommendationsModal) closeRecommendationsModal();
  });
}

window.switchRecTab = async function (category) {
  state.activeRecCategory = category;
  if (category === "food") {
    if (recTabFood) recTabFood.classList.add("active");
    if (recTabEntertainment) recTabEntertainment.classList.remove("active");
  } else {
    if (recTabEntertainment) recTabEntertainment.classList.add("active");
    if (recTabFood) recTabFood.classList.remove("active");
  }
  await loadPollRecommendations(category);
};

window.loadPollRecommendations = async function (category) {
  if (!state.activeRecPoll || !state.token) return;
  const { pollId, groupId } = state.activeRecPoll;
  const cacheKey = `${pollId}_${category}`;

  if (recCardsList) recCardsList.innerHTML = "";
  if (recLoadingSpinner) recLoadingSpinner.classList.remove("hidden");
  if (recItemsCount) recItemsCount.textContent = "Searching...";

  try {
    let data = state.recCache[cacheKey];
    if (!data) {
      const res = await fetch(`/api/groups/${groupId}/hangouts/${pollId}/recommendations?category=${category}`, {
        headers: {
          Authorization: `Bearer ${state.token}`,
        },
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to load recommendations.");
      }
      data = await res.json();
      state.recCache[cacheKey] = data;
    }

    renderRecommendationsList(data);
  } catch (err) {
    if (recLoadingSpinner) recLoadingSpinner.classList.add("hidden");
    if (recCardsList) {
      recCardsList.innerHTML = `
        <div style="text-align: center; padding: 2rem 1rem; color: #f87171;">
          <p style="font-size: 0.9rem;">⚠️ Failed to load options: ${escapeHtml(err.message)}</p>
          <button type="button" class="btn-refresh" style="margin-top: 0.5rem;" onclick="loadPollRecommendations('${category}')">Try Again</button>
        </div>
      `;
    }
  }
};

function renderRecommendationsList(data) {
  if (recLoadingSpinner) recLoadingSpinner.classList.add("hidden");
  if (!recCardsList) return;

  // Midpoint display
  if (recMidpointText && data.midpoint) {
    recMidpointText.textContent = `Group Midpoint: ${data.midpoint.lat.toFixed(4)}, ${data.midpoint.lon.toFixed(4)}`;
  } else if (recMidpointText) {
    recMidpointText.textContent = data.midpoint_address || "Calculated from members";
  }

  // Missing address warning
  if (recMissingAddressWarning && recMissingUsersList) {
    if (data.missing_addresses && data.missing_addresses.length > 0) {
      recMissingUsersList.textContent = data.missing_addresses.join(", ");
      recMissingAddressWarning.classList.remove("hidden");
    } else if (data.missing_address_users && data.missing_address_users.length > 0) {
      recMissingUsersList.textContent = data.missing_address_users.map((u) => `@${u}`).join(", ");
      recMissingAddressWarning.classList.remove("hidden");
    } else {
      recMissingAddressWarning.classList.add("hidden");
    }
  }

  // Source notice: clearly indicate whether live or sample data
  if (recSourceNotice && recSourceText) {
    recSourceNotice.classList.remove("hidden");
    if (data.is_mock_data || data.is_mock) {
      recSourceNotice.style.background = "rgba(245, 158, 11, 0.08)";
      recSourceNotice.style.border = "1px solid rgba(245, 158, 11, 0.25)";
      recSourceNotice.style.color = "#fbbf24";
      if (recSourceIcon) recSourceIcon.textContent = "⚡";
      recSourceText.innerHTML = `<strong>Demo Mode (Sample Data):</strong> Showing simulated verified venues. Live streaming is active when Google Places & Ticketmaster API keys are configured.`;
    } else {
      recSourceNotice.style.background = "rgba(59, 130, 246, 0.09)";
      recSourceNotice.style.border = "1px solid rgba(59, 130, 246, 0.28)";
      recSourceNotice.style.color = "#93c5fd";
      if (recSourceIcon) recSourceIcon.textContent = "🌐";
      recSourceText.innerHTML = `<strong>Live Stream:</strong> Verified live results from Google Places & Ticketmaster Discovery APIs.`;
    }
  }

  // Raw items from server
  const rawItems = (data.items || []).slice();

  // Apply Client-Side Budget Filter
  const budgetFilter = (state.recFilters && state.recFilters.budget) || "all";
  let items = rawItems.filter((item) => {
    if (budgetFilter === "all") return true;
    const tier = item.price_tier != null ? item.price_tier : 2;
    if (budgetFilter === "$") return tier <= 1;
    if (budgetFilter === "$$") return tier === 2;
    if (budgetFilter === "$$$") return tier >= 3;
    return true;
  });

  // Apply Client-Side Distance Filter
  const maxDist = state.recFilters && state.recFilters.maxDistance;
  if (maxDist != null && maxDist > 0) {
    items = items.filter((item) => item.avg_distance_miles <= maxDist);
  }

  // Apply Within Limits Only Filter
  if (state.recFilters && state.recFilters.withinLimitsOnly) {
    items = items.filter((item) => item.all_within_limit === true);
  }

  // Apply Sorting
  const sortBy = (state.recFilters && state.recFilters.sortBy) || "recommended";
  if (sortBy === "distance") {
    items.sort((a, b) => a.avg_distance_miles - b.avg_distance_miles);
  } else if (sortBy === "rating") {
    items.sort((a, b) => (b.rating || 0) - (a.rating || 0));
  } else if (sortBy === "budget") {
    items.sort((a, b) => ((a.price_tier ?? 2) - (b.price_tier ?? 2)) || a.avg_distance_miles - b.avg_distance_miles);
  } else {
    // "recommended" default: respect limits first, then top ratings, then lowest distance
    items.sort((a, b) => {
      if (a.all_within_limit !== b.all_within_limit) {
        return a.all_within_limit ? -1 : 1;
      }
      const diffRating = (b.rating || 0) - (a.rating || 0);
      if (Math.abs(diffRating) > 0.05) return diffRating;
      return a.avg_distance_miles - b.avg_distance_miles;
    });
  }

  if (recItemsCount) {
    recItemsCount.textContent = `${items.length} of ${rawItems.length} options match filters`;
  }

  if (items.length === 0) {
    recCardsList.innerHTML = `
      <div style="text-align: center; padding: 2.5rem 1rem; color: var(--text-muted);">
        <p style="font-size: 0.95rem; margin-bottom: 0.4rem;">No matching venues found for these budget and distance filters.</p>
        <p style="font-size: 0.78rem;">Try selecting "All Budgets" or choosing a wider distance radius.</p>
      </div>
    `;
    return;
  }

  const poll = state.activeRecPoll ? state.currentGroupPolls[state.activeRecPoll.pollId] : null;

  // Build place vote lookup for quick rendering
  const placeVoteLookup = {};
  if (poll && poll.place_votes) {
    for (const pv of poll.place_votes) {
      placeVoteLookup[pv.place_name.toLowerCase()] = pv;
    }
  }

  recCardsList.innerHTML = items.map((item, idx) => {
    const itemTitleLower = item.title.trim().toLowerCase();
    const pvInfo = placeVoteLookup[itemTitleLower];
    const voteCount = pvInfo ? pvInfo.count : 0;
    const hasVoted = Boolean(
      (pvInfo && pvInfo.has_voted) ||
      (poll && poll.my_place_votes && poll.my_place_votes.map((p) => p.toLowerCase()).includes(itemTitleLower))
    );
    const votersList = pvInfo && pvInfo.voters && pvInfo.voters.length ? pvInfo.voters.join(", @") : "";

    // SCRUM-52: Star Rating & Review Count Summary
    const reviewsList = Array.isArray(item.reviews) ? item.reviews : [];
    const totalReviews = item.user_rating_count || reviewsList.length;
    const ratingStars = item.rating ? `★ ${item.rating.toFixed(1)}` : "★ New";
    const reviewCountText = totalReviews > 0 ? ` (${totalReviews} reviews)` : "";

    // Budget Price Badge
    let priceClass = "tier-2";
    if (item.price_tier === 0 || item.price_level === "Free") priceClass = "free";
    else if (item.price_tier === 1) priceClass = "tier-1";
    else if (item.price_tier === 2) priceClass = "tier-2";
    else if (item.price_tier === 3) priceClass = "tier-3";
    else if (item.price_tier >= 4) priceClass = "tier-4";

    const priceBadge = item.price_level
      ? `<span class="rec-price-badge ${priceClass}">${escapeHtml(item.price_display || item.price_level)}</span>`
      : "";

    // Match reasons chips
    const matchReasonsHtml = (item.match_reasons || []).map((r) => {
      return `<span class="rec-match-chip">${escapeHtml(r)}</span>`;
    }).join("");

    const openBadge = item.is_open_confirmed
      ? `<span class="rec-badge-open">✓ ${escapeHtml(item.open_hours_text || "Verified Open")}</span>`
      : `<span class="badge" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24;">Hours Unverified</span>`;

    const sourceBadge = item.is_mock
      ? `<span class="rec-badge-mock" title="Sample demo item (API keys not configured)">⚡ Sample</span>`
      : `<span class="rec-badge-live" title="Live data verified from ${escapeHtml(item.source || 'API')}">● Live</span>`;

    const eventBadge = item.item_type === "event"
      ? `<span class="rec-badge-event">🎟 ${escapeHtml(item.event_time || "Live Event")}</span>`
      : "";

    const commutePills = (item.user_distances || []).map((ud) => {
      const cls = ud.is_within_limit ? "ok" : "exceeded";
      const icon = ud.is_within_limit ? "✓" : "⚠";
      return `
        <span class="rec-commute-pill ${cls}" title="${ud.is_within_limit ? 'Within max travel limit' : `Exceeds max limit (${ud.max_distance_miles} mi)`}">
          ${icon} @${escapeHtml(ud.username)}: ${ud.distance_miles} mi
        </span>
      `;
    }).join("");

    // Activity Information Drawer HTML
    const infoDrawerId = `rec-info-drawer-${idx}`;
    const hoursListHtml = (item.weekday_hours && item.weekday_hours.length > 0)
      ? item.weekday_hours.map((h) => `<div>${escapeHtml(h)}</div>`).join("")
      : `<div>${escapeHtml(item.open_hours_text || "Open during scheduled hangout window")}</div>`;

    const infoDrawerHtml = `
      <div id="${infoDrawerId}" class="rec-drawer-box hidden">
        <div class="rec-info-grid">
          <div class="rec-info-row">
            <span class="rec-info-label">Category & Budget</span>
            <span class="rec-info-val">${escapeHtml(item.category)} (${escapeHtml(item.subcategory)}) • ${escapeHtml(item.price_display || item.price_level || "$$")}</span>
          </div>
          <div class="rec-info-row">
            <span class="rec-info-label">Distance Overview</span>
            <span class="rec-info-val">${item.avg_distance_miles} mi avg commute (${item.min_member_distance_miles ?? item.avg_distance_miles} mi min / ${item.max_member_distance_miles ?? item.avg_distance_miles} mi max)</span>
          </div>
          <div class="rec-info-row">
            <span class="rec-info-label">Address</span>
            <span class="rec-info-val">${escapeHtml(item.address || "Address on map")}</span>
          </div>
          <div class="rec-info-row">
            <span class="rec-info-label">Phone Number</span>
            <span class="rec-info-val">
              ${item.phone_number ? `<a href="tel:${escapeHtml(item.phone_number)}">${escapeHtml(item.phone_number)}</a>` : "Not listed"}
            </span>
          </div>
          <div class="rec-info-row">
            <span class="rec-info-label">Official Links</span>
            <span class="rec-info-val" style="display: flex; gap: 0.6rem; flex-wrap: wrap;">
              ${item.website_url ? `<a href="${escapeHtml(item.website_url)}" target="_blank" rel="noopener noreferrer">Website ↗</a>` : ""}
              ${item.maps_url ? `<a href="${escapeHtml(item.maps_url)}" target="_blank" rel="noopener noreferrer">Google Maps ↗</a>` : ""}
              ${item.ticket_url ? `<a href="${escapeHtml(item.ticket_url)}" target="_blank" rel="noopener noreferrer">Tickets ↗</a>` : ""}
            </span>
          </div>
        </div>
        <div class="rec-info-row" style="margin-top: 0.55rem; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06);">
          <span class="rec-info-label">Operating Hours</span>
          <div class="rec-info-val" style="font-size: 0.73rem; color: var(--text-secondary); line-height: 1.4;">
            ${hoursListHtml}
          </div>
        </div>
      </div>
    `;

    // Activity Reviews Drawer HTML
    const reviewsDrawerId = `rec-reviews-drawer-${idx}`;
    const reviewsItemsHtml = reviewsList.length > 0
      ? reviewsList.map((r) => {
          const initial = (r.author_name || "U")[0].toUpperCase();
          const starsVisual = "★".repeat(Math.round(r.rating || 5)) + "☆".repeat(Math.max(0, 5 - Math.round(r.rating || 5)));
          return `
            <div class="rec-review-item">
              <div class="rec-review-header">
                <span class="rec-reviewer-badge">
                  <span class="rec-reviewer-avatar">${escapeHtml(initial)}</span>
                  <span>${escapeHtml(r.author_name)}</span>
                </span>
                <span style="font-size: 0.7rem; color: var(--text-muted);">
                  <span style="color: #fbbf24; margin-right: 0.3rem;">${starsVisual}</span>
                  ${escapeHtml(r.relative_time || "Recently")}
                </span>
              </div>
              <p style="margin: 0; color: var(--text-secondary); line-height: 1.4;">
                "${escapeHtml(r.text)}"
              </p>
            </div>
          `;
        }).join("")
      : `<p style="margin: 0; color: var(--text-muted); font-style: italic;">No written reviews available for this venue yet.</p>`;

    const reviewsDrawerHtml = `
      <div id="${reviewsDrawerId}" class="rec-drawer-box hidden">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; padding-bottom: 0.35rem; border-bottom: 1px solid rgba(255,255,255,0.08);">
          <strong style="color: var(--text-main); font-size: 0.78rem;">Customer Reviews (${reviewsList.length} shown)</strong>
          <span style="color: #fbbf24; font-weight: 700; font-size: 0.76rem;">${ratingStars}${escapeHtml(reviewCountText)}</span>
        </div>
        ${reviewsItemsHtml}
      </div>
    `;

    const voteBtnTitle = votersList ? `Voted by: @${escapeHtml(votersList)}` : (hasVoted ? "Click to remove your vote" : "Vote for this place");
    const voteBtnHtml = `
      <button
        type="button"
        class="btn-place-vote ${hasVoted ? 'voted' : ''}"
        onclick="castPlaceVote(${data.group_id}, ${data.poll_id}, '${escapeHtml(item.title).replace(/'/g, "\\'")}')"
        title="${voteBtnTitle}"
      >
        <span>${hasVoted ? '✓ Voted Yes' : '👍 Vote Yes'}</span>
        <span class="place-vote-count-badge">${voteCount}</span>
      </button>
    `;

    return `
      <div class="rec-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.3rem; gap: 0.5rem;">
          <div>
            <div style="display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap;">
              <strong style="font-size: 0.95rem; color: var(--text-main);">${escapeHtml(item.title)}</strong>
              ${priceBadge}
              ${sourceBadge}
              ${openBadge}
              ${eventBadge}
            </div>
            <div style="font-size: 0.76rem; color: var(--text-muted); margin-top: 0.2rem;">
              <span style="color: #fbbf24; font-weight: 600;">${ratingStars}</span><span style="color: var(--text-muted);">${escapeHtml(reviewCountText)}</span> • <span style="color: var(--text-secondary);">${escapeHtml(item.subcategory)}</span>
            </div>
            ${matchReasonsHtml ? `<div style="display: flex; gap: 0.3rem; flex-wrap: wrap; margin-top: 0.35rem;">${matchReasonsHtml}</div>` : ""}
          </div>
          <div style="text-align: right; flex-shrink: 0;">
            <span style="font-size: 0.78rem; font-weight: 700; color: var(--accent); display: block;">${item.avg_distance_miles} mi avg</span>
            <span style="font-size: 0.7rem; color: ${item.all_within_limit ? '#34d399' : '#fbbf24'};">${item.all_within_limit ? 'All members in range' : 'Partial range'}</span>
          </div>
        </div>

        ${item.description ? `<p class="rec-description-text">${escapeHtml(item.description)}</p>` : ""}

        <p style="font-size: 0.75rem; color: var(--text-muted); margin: 0 0 0.5rem 0;">
          📍 ${escapeHtml(item.address)}
        </p>

        <!-- Activity Action Buttons -->
        <div class="rec-action-bar">
          <button type="button" class="btn-rec-drawer-toggle" onclick="toggleRecDrawer('${infoDrawerId}', this)">
            ℹ️ Activity Info
          </button>
          <button type="button" class="btn-rec-drawer-toggle" onclick="toggleRecDrawer('${reviewsDrawerId}', this)">
            💬 Reviews (${reviewsList.length})
          </button>
          ${item.maps_url ? `<a href="${escapeHtml(item.maps_url)}" target="_blank" rel="noopener noreferrer" class="btn-rec-drawer-toggle" style="text-decoration: none;">🗺️ Open Map</a>` : ""}
          ${item.website_url ? `<a href="${escapeHtml(item.website_url)}" target="_blank" rel="noopener noreferrer" class="btn-rec-drawer-toggle" style="text-decoration: none;">🌐 Website</a>` : ""}
        </div>

        ${infoDrawerHtml}
        ${reviewsDrawerHtml}

        <div style="display: flex; flex-wrap: wrap; gap: 0.35rem; align-items: center; margin-bottom: 0.65rem;">
          <span style="font-size: 0.7rem; color: var(--text-muted); margin-right: 0.2rem;">Commutes:</span>
          ${commutePills}
        </div>
        <div style="display: flex; gap: 0.5rem; align-items: center; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.5rem;">
          <span style="font-size: 0.72rem; color: var(--text-muted);">
            ${votersList ? `Voters: @${escapeHtml(votersList)}` : 'No votes yet for this venue'}
          </span>
          ${voteBtnHtml}
        </div>
      </div>
    `;
  }).join("");
}

window.toggleRecDrawer = function (drawerId, btnEl) {
  const drawer = document.getElementById(drawerId);
  if (!drawer) return;
  const isHidden = drawer.classList.toggle("hidden");
  if (btnEl) {
    btnEl.classList.toggle("active", !isHidden);
  }
};

window.castPlaceVote = async function (groupId, pollId, placeName) {
  if (!state.token) return;
  try {
    const res = await fetch(`/api/groups/${groupId}/hangouts/${pollId}/place-vote`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${state.token}`,
      },
      body: JSON.stringify({ place_name: placeName }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to vote on place.");
    }
    const updatedPoll = await res.json();
    updatePollCardDOM(updatedPoll);
    
    // Update local cache or re-render active recommendations modal
    const cacheKey = `${pollId}_${state.activeRecCategory || 'food'}`;
    const cachedData = state.recCache[cacheKey];
    if (cachedData) {
      renderRecommendationsList(cachedData);
    }
    showToast(`Vote updated for "${placeName}"!`, "success");
  } catch (err) {
    showToast(err.message, "error");
  }
};

window.setRecommendationAsPlace = async function (groupId, pollId, itemTitle) {
  if (!state.token) return;
  try {
    const res = await fetch(`/api/groups/${groupId}/hangouts/${pollId}/place`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${state.token}`,
      },
      body: JSON.stringify({ text: itemTitle }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to update place.");
    }
    const updatedPoll = await res.json();
    updatePollCardDOM(updatedPoll);
    showToast(`Updated hangout place to "${itemTitle}"!`, "success");
    await loadPollRecommendations(state.activeRecCategory || "food");
  } catch (err) {
    showToast(err.message, "error");
  }
};

window.suggestRecommendationToLeader = function (itemTitle) {
  showToast(`"${itemTitle}" suggested! Only group leaders can add options to this poll.`, "info");
};

// ==================== INTERACTIVE GROUP MAP ====================
let groupMap = null;
let meetupPinMarker = null;

function initOrRefreshGroupMap() {
  const mapEl = document.getElementById("group-interactive-map");
  if (!mapEl || typeof L === "undefined") return;

  if (!groupMap) {
    // Centered on Northridge / LA
    groupMap = L.map("group-interactive-map").setView([34.2381, -118.5277], 11);

    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
      maxZoom: 19,
    }).addTo(groupMap);

    // Drop a pin when clicking the map
    groupMap.on("click", (e) => {
      const { lat, lng } = e.latlng;
      setMeetupPin(lat, lng, `<strong>Meetup Pin</strong><br><small>${lat.toFixed(4)}, ${lng.toFixed(4)}</small>`);
    });

    const btnCenterMe = document.getElementById("btn-center-my-location");
    if (btnCenterMe) {
      btnCenterMe.addEventListener("click", () => {
        if (!navigator.geolocation) {
          showToast("Geolocation is not supported by your browser.", "error");
          return;
        }
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            const { latitude, longitude } = pos.coords;
            groupMap.flyTo([latitude, longitude], 13);
            setMeetupPin(latitude, longitude, "<strong>You are here</strong>");
          },
          () => showToast("Could not access your location.", "error")
        );
      });
    }
  }

  // Fixes gray/cut-off tiles when unhiding the tab
  setTimeout(() => {
    groupMap.invalidateSize();
  }, 150);
}

function setMeetupPin(lat, lng, labelHtml) {
  if (!groupMap) return;
  if (meetupPinMarker) {
    meetupPinMarker.setLatLng([lat, lng]).setPopupContent(labelHtml).openPopup();
  } else {
    meetupPinMarker = L.marker([lat, lng]).addTo(groupMap).bindPopup(labelHtml).openPopup();
  }
}
// Boot application
switchTab("login");
checkEmailVerificationParam();
checkPasswordResetParam();
checkExistingSession();