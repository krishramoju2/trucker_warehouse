// Example: Submit new employee form
async function submitEmployeeForm(event) {
  event.preventDefault();

  const data = {
    name: document.getElementById("name").value,
    date_of_birth: document.getElementById("dob").value,
    address: document.getElementById("address").value,
    contact_number: document.getElementById("contact").value,
    pan_number: document.getElementById("pan").value,
    aadhar_number: document.getElementById("aadhar").value,
  };

  const response = await fetch("http://localhost:8080/employee", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  const result = await response.json();
  alert("Employee created: " + JSON.stringify(result));
}

// Example: Upload files
async function uploadDocuments(event, employeeId) {
  event.preventDefault();

  const formData = new FormData();
  formData.append("resume", document.getElementById("resume").files[0]);
  formData.append("educational_certificates", document.getElementById("certs").files[0]);
  formData.append("offer_letters", document.getElementById("offer").files[0]);
  formData.append("pan_card", document.getElementById("pan_card").files[0]);
  formData.append("aadhar_card", document.getElementById("aadhar_card").files[0]);
  formData.append("form_16_or_it_returns", document.getElementById("form16").files[0]);

  const response = await fetch(`http://localhost:8080/upload/${employeeId}`, {
    method: "POST",
    body: formData,
  });

  const result = await response.json();
  alert("Documents uploaded: " + JSON.stringify(result));
}
