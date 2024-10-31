const uploadContainer = document.getElementById("uploadContainer");
const fileInput = document.getElementById("fileInput");
const uploadButton = document.getElementById("uploadButton");
let file; // Store the file for uploading

// Drag-and-drop events
uploadContainer.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadContainer.classList.add("drag-over");
});

uploadContainer.addEventListener("dragleave", () => {
    uploadContainer.classList.remove("drag-over");
});

uploadContainer.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadContainer.classList.remove("drag-over");
    file = e.dataTransfer.files[0];
    displayFileName(file.name);
});

// File input change event (for browsing)
fileInput.addEventListener("change", (e) => {
    file = e.target.files[0];
    displayFileName(file.name);
});

// Display selected file name
function displayFileName(name) {
    uploadContainer.innerHTML = `<p>Selected: ${name}</p>`;
}

// Upload button click event
uploadButton.addEventListener("click", () => {
    if (!file) {
        alert("Please select a file first.");
        return;
    }
    uploadFile(file);
});

// Function to upload the file
async function uploadFile(file) {
    const formData = new FormData();
    formData.append("image", file);

    const response = await fetch("/upload", {
        method: "POST",
        body: formData
    });

    if (response.ok) {
        alert("Image uploaded successfully!");
    } else {
        alert("Image upload failed. Please try again.");
    }
}
