function showDialog() {
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('alert-dialog').style.display = 'block';
}

function closeDialog() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('alert-dialog').style.display = 'none';
}
function goToPage(url) { window.location.href = url; }