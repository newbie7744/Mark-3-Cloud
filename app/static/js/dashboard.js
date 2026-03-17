// =======================
// DATE & TIME (KEEP)
// =======================
function updateTime() {
    const now = new Date();

    document.getElementById("date").innerText =
        now.toLocaleDateString();

    document.getElementById("time").innerText =
        now.toLocaleTimeString();
}

setInterval(updateTime, 1000);
updateTime();


// =======================
// FILE UPLOAD WITH PROGRESS
// =======================
function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload_file", true);

    // 🔥 Progress tracking
    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);

            const bar = document.getElementById("progressBar");
            bar.style.width = percent + "%";
            bar.innerText = percent + "%";
        }
    };

    // ✅ Upload complete
    xhr.onload = function () {
        if (xhr.status === 200 || xhr.status === 302) {
            // Reset progress
            const bar = document.getElementById("progressBar");
            bar.style.width = "0%";
            bar.innerText = "0%";

            // Refresh dashboard
            window.location.href = "/dashboard";
        } else {
            alert("Upload failed");
        }
    };

    xhr.onerror = function () {
        alert("Something went wrong!");
    };

    xhr.send(formData);
}