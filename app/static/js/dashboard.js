// =======================
// DOM READY
// =======================
document.addEventListener("DOMContentLoaded", function () {

    // Upload button click
    const uploadBtn = document.getElementById("uploadBtn");
    if (uploadBtn) {
        uploadBtn.addEventListener("click", uploadFile);
    }

    // Menu toggle
    document.querySelectorAll(".menu-btn").forEach(btn => {
        btn.addEventListener("click", function(e) {
            e.stopPropagation();
            toggleMenu(this);
        });
    });

    // Rename buttons
    document.querySelectorAll(".rename-btn").forEach(btn => {
        btn.addEventListener("click", function() {
            showRename(this);
        });
    });

    // Cancel rename buttons
    document.querySelectorAll(".cancel-rename-btn").forEach(btn => {
        btn.addEventListener("click", function() {
            cancelRename(this);
        });
    });

    // Profile menu button
    const profileMenuBtn = document.querySelector(".profile-menu-btn");
    if (profileMenuBtn) {
        profileMenuBtn.addEventListener("click", function(e) {
            e.stopPropagation();
            toggleProfileMenu(this);
        });
    }

    // Close menus on outside click
    document.addEventListener("click", function () {
        document.querySelectorAll(".menu-content, .profile-menu-content").forEach(m => m.style.display = "none");
    });

    // Start date/time
    updateTime();
    setInterval(updateTime, 1000);
});

// =======================
// DATE & TIME
// =======================
function updateTime() {
    const now = new Date();
    const day = String(now.getDate()).padStart(2, '0');
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const year = now.getFullYear();
    document.getElementById("date").innerText = `${day}-${month}-${year}`;
    document.getElementById("time").innerText = now.toLocaleTimeString();
}

// =======================
// FILE UPLOAD FUNCTION
// =======================
function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const files = Array.from(fileInput.files || []);
    if (files.length === 0) {
        alert("Please select one or more files");
        return;
    }

    const formData = new FormData();
    files.forEach(file => {
        const relativeName = file.webkitRelativePath && file.webkitRelativePath.length > 0
            ? file.webkitRelativePath
            : file.name;
        formData.append("files", file, relativeName);
    });

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload_file", true);

    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            const bar = document.getElementById("progressBar");
            bar.style.width = percent + "%";
            bar.innerText = percent + "%";
        }
    };

    xhr.onload = function () {
        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                if (response.message && response.message.indexOf("uploaded successfully") !== -1) {
                    window.location.href = "/dashboard";
                } else {
                    alert("Upload failed: " + (response.message || "Unknown error"));
                }
            } catch (e) {
                alert("Upload failed: Invalid response");
            }
        } else {
            alert("Upload failed with status " + xhr.status);
        }
    };

    xhr.onerror = function () {
        alert("Something went wrong!");
    };

    xhr.send(formData);
}

// =======================
// MENU FUNCTIONS
// =======================
function toggleMenu(button) {
    const menu = button.nextElementSibling;
    document.querySelectorAll(".menu-content").forEach(m => {
        if (m !== menu) m.style.display = "none";
    });
    menu.style.display = (menu.style.display === "block") ? "none" : "block";
}

function showRename(button) {
    const form = button.nextElementSibling;
    form.style.display = "block";
    const input = form.querySelector("input");
    if (input) input.focus();
}

function cancelRename(button) {
    const form = button.closest(".rename-form");
    form.style.display = "none";
    const input = form.querySelector("input");
    if (input) input.value = "";
}

// =======================
// PROFILE MENU FUNCTIONS
// =======================
function toggleProfileMenu(button) {
    const menu = button.nextElementSibling;
    const isVisible = menu.style.display === "block";
    document.querySelectorAll(".menu-content, .profile-menu-content").forEach(m => m.style.display = "none");
    if (!isVisible) {
        menu.style.display = "block";
    }
}

function toggleChangeForm() {
    const form = document.querySelector(".profile-edit-form");
    if (form) {
        form.style.display = form.style.display === "flex" ? "none" : "flex";
    }
}