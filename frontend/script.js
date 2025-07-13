// 🚀 Submit new employee form
async function submitEmployeeForm(event) {
  event.preventDefault();

  const submitBtn = document.getElementById("submitEmployeeBtn");
  submitBtn.disabled = true;

  const data = {
    name: document.getElementById("name").value.trim(),
    date_of_birth: document.getElementById("dob").value,
    address: document.getElementById("address").value.trim(),
    contact_number: document.getElementById("contact").value.trim(),
    pan_number: document.getElementById("pan").value.trim(),
    aadhar_number: document.getElementById("aadhar").value.trim(),
  };

  try {
    const response = await fetch("http://localhost:8080/employee", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to create employee.");
    }

    const result = await response.json();
    alert("✅ Employee created successfully! ID: " + result.id);
    event.target.reset();
  } catch (err) {
    alert("❌ Error: " + err.message);
  } finally {
    submitBtn.disabled = false;
  }
}

document.getElementById("registerForm")?.addEventListener("submit", submitEmployeeForm);

// 📁 Upload employee documents
async function uploadDocuments(event) {
  event.preventDefault();

  const uploadBtn = document.getElementById("uploadBtn");
  uploadBtn.disabled = true;

  const empid = document.getElementById("empid").value;
  const formData = new FormData();
  formData.append("resume", document.getElementById("resume").files[0]);
  formData.append("educational_certificates", document.getElementById("certs").files[0]);
  formData.append("offer_letters", document.getElementById("offer").files[0]);
  formData.append("pan_card", document.getElementById("pan_card").files[0]);
  formData.append("aadhar_card", document.getElementById("aadhar_card").files[0]);
  formData.append("form_16_or_it_returns", document.getElementById("form16").files[0]);

  try {
    const response = await fetch(`http://localhost:8080/files/upload/${empid}`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to upload documents.");
    }

    const result = await response.json();
    alert("📦 Documents uploaded successfully!");
    event.target.reset();
  } catch (err) {
    alert("❌ Error uploading files: " + err.message);
  } finally {
    uploadBtn.disabled = false;
  }
}

document.getElementById("uploadForm")?.addEventListener("submit", uploadDocuments);

