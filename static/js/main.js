async function updateStatus() {
  const statusElement = document.getElementById('status');
  try {
    const response = await fetch('/healthz');
    const data = await response.json();
    statusElement.textContent = `Health: ${data.status}`;
  } catch (error) {
    statusElement.textContent = 'Health: unavailable';
  }
}

updateStatus();


