function copyLink() {
  const link = window.location.href;
  navigator.clipboard.writeText(link).then(() => {
    alert("Link copied!");
  });
}

function generateQR(url) {
  const modal = document.getElementById("qrModal");
  const canvasDiv = document.getElementById("qrCanvas");
  canvasDiv.innerHTML = "";
  QRCode.toDataURL(url)
    .then(dataUrl => {
      const img = document.createElement("img");
      img.src = dataUrl;
      img.alt = "QR code";
      canvasDiv.appendChild(img);
      modal.classList.remove("hidden");
      modal.classList.add("flex");
    })
    .catch(err => console.error(err));
}

function closeQR() {
  const modal = document.getElementById("qrModal");
  modal.classList.add("hidden");
  modal.classList.remove("flex");
}
