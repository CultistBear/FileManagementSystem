function renameFile(button) {
  var newName = prompt("Enter new file name:");
  if (newName !== null) {
      console.log(newName);
      button.form.elements["Rename_new"].value = newName;
      button.form.elements["Rename"].click();
  } else {
      alert("No input provided.");
  }
}


function displayLink(button){
    console.log(button.form.elements["Share"].value);
    button.form.elements["Share"].click();
}

window.onload = function() {
    // Access the global variable set in the HTML template
    var flag = window.flag;
    if (flag === 1){
        var formPopup = document.getElementById("ShareLinks");
        var overlay = document.getElementById("overlay");
        if (formPopup.style.display === "none" || formPopup.style.display === "" || overlay.style.display === "" || overlay.style.display === "none") {
            formPopup.style.display = "block"; // Show the form
            overlay.style.display = "block"; // Show the overlay
            document.body.style.overflow = "hidden"; // Prevent scrolling
            setTimeout(function () {
                overlay.style.opacity = "1"; // Fade in the overlay
            }, 10);
        } else {
            formPopup.style.display = "none"; // Hide the form
            overlay.style.opacity = "0"; // Fade out the overlay
            document.body.style.overflow = ""; // Restore scrolling
            setTimeout(function () {
            overlay.style.display = "none"; // Hide the overlay after fading out
            }, 300); // Match transition duration
        }
    }
};

// Close the form when clicking outside of it
window.addEventListener("click", function (event) {
    var formPopup = document.getElementById("wtfForm");
    var overlay = document.getElementById("overlay");
    if (event.target == overlay) {
        formPopup.style.display = "none";
        overlay.style.display = "none";
        overlay.style.opacity = "0";
        document.body.style.overflow = ""; // Restore scrolling
    }
  });
window.addEventListener("click", function (event) {
    var formPopup = document.getElementById("ShareLinks");
    var overlay = document.getElementById("overlay");
    if (event.target == overlay) {
        formPopup.style.display = "none";
        overlay.style.display = "none";
        overlay.style.opacity = "0";
        document.body.style.overflow = ""; // Restore scrolling
    }
  });
  



function shareFile(button) {
  var formPopup = document.getElementById("ShareLinks");
  var overlay = document.getElementById("overlay");
  if (formPopup.style.display === "none" || formPopup.style.display === "") {
      formPopup.style.display = "block"; // Show the form
      overlay.style.display = "block"; // Show the overlay
      document.body.style.overflow = "hidden"; // Prevent scrolling
      setTimeout(function () {
          overlay.style.opacity = "1"; // Fade in the overlay
      }, 10);
  } else {
      formPopup.style.display = "none"; // Hide the form
      overlay.style.opacity = "0"; // Fade out the overlay
      document.body.style.overflow = ""; // Restore scrolling
      setTimeout(function () {
          overlay.style.display = "none"; // Hide the overlay after fading out
      }, 300); // Match transition duration
  }
}



function uploadFile(button) {
  var formPopup = document.getElementById("wtfForm");
  var overlay = document.getElementById("overlay");
  if (formPopup.style.display === "none" || formPopup.style.display === "") {
      formPopup.style.display = "block"; // Show the form
      overlay.style.display = "block"; // Show the overlay
      document.body.style.overflow = "hidden"; // Prevent scrolling
      setTimeout(function () {
          overlay.style.opacity = "1"; // Fade in the overlay
      }, 10);
  } else {
      formPopup.style.display = "none"; // Hide the form
      overlay.style.opacity = "0"; // Fade out the overlay
      document.body.style.overflow = ""; // Restore scrolling
      setTimeout(function () {
          overlay.style.display = "none"; // Hide the overlay after fading out
      }, 300); // Match transition duration
  }
}




