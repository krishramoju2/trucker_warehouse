// ✅ Register Employee
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

// 📁 Upload Documents
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

// 🔍 Search Employee by ID
document.getElementById("searchInput")?.addEventListener("input", async (e) => {
  const query = e.target.value.trim();
  const resultsList = document.getElementById("resultsList");
  resultsList.innerHTML = '';

  if (query === '') return;

  try {
    const response = await fetch(`http://localhost:8080/employee/${query}`);
    if (!response.ok) {
      const li = document.createElement('li');
      li.textContent = "No matching employee found.";
      resultsList.appendChild(li);
      return;
    }

    const emp = await response.json();
    const li = document.createElement('li');
    li.textContent = `ID: ${emp.id} | Name: ${emp.name} | DOB: ${emp.date_of_birth} | Contact: ${emp.contact_number} | Address: ${emp.address} | PAN: ${emp.pan_number} | Aadhar: ${emp.aadhar_number}`;
    resultsList.appendChild(li);
  } catch (err) {
    const li = document.createElement('li');
    li.textContent = "Error fetching employee.";
    resultsList.appendChild(li);
    console.error(err);
  }
});

// 📊 Load Dashboard Stats
async function loadStats() {
  const empCountEl = document.getElementById("empCount");
  const docCountEl = document.getElementById("docCount");
  const empBar = document.getElementById("empBar");
  const docBar = document.getElementById("docBar");

  if (!empCountEl || !docCountEl || !empBar || !docBar) return;

  try {
    const empRes = await fetch('http://localhost:8080/stats/employees');
    const docRes = await fetch('http://localhost:8080/stats/documents');

    if (!empRes.ok || !docRes.ok) throw new Error("Failed to fetch stats");

    const empData = await empRes.json();
    const docData = await docRes.json();

    const empCount = empData.count || 0;
    const docCount = docData.count || 0;

    empCountEl.innerText = empCount;
    docCountEl.innerText = docCount;

    empBar.style.width = Math.min(empCount * 10, 100) + "%";
    docBar.style.width = Math.min(docCount * 10, 100) + "%";
  } catch (err) {
    console.error("Dashboard Load Error:", err);
    alert("❌ Could not load dashboard stats.");
  }
}

document.addEventListener("DOMContentLoaded", loadStats);

