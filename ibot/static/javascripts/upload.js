function fileSelected() {
  var file = document.getElementById('fileToUpload').files[0];
  if (file) {
    var fileSize = 0;
    if (file.size > 1024 * 1024)
      fileSize = (Math.round(file.size * 100 / (1024 * 1024)) / 100).toString() + 'MB';
    else
      fileSize = (Math.round(file.size * 100 / 1024) / 100).toString() + 'KB';
    document.getElementById('fileName').innerHTML = 'FileName: ' + file.name;
    document.getElementById('fileSize').innerHTML = 'FileSize: ' + fileSize;
    document.getElementById('fileType').innerHTML = 'FileType:' + file.type;
    setProcess('0');
    }
}

function uploadFile() {
  var fd = new FormData();
  fd.append("file", document.getElementById('fileToUpload').files[0]);
  var xhr = new XMLHttpRequest();
  xhr.upload.addEventListener("progress", uploadProgress, false);
  xhr.addEventListener("load", uploadComplete, false);
  xhr.addEventListener("error", uploadFailed, false);
  xhr.addEventListener("abort", uploadCanceled, false);
  xhr.open("POST", "/upload", true);
  xhr.send(fd);
}

function uploadProgress(evt) {
  if(evt.lengthComputable) {
    var percentComplete = Math.round(evt.loaded * 100 / evt.total);
    setProcess(percentComplete.toString());
  }
  else {
    document.getElementById('progressNumber').innerHTML = 'unable to compute';
  }
}

function uploadComplete(evt) {
  setProcess('100');
  alert(evt.target.responseText);
}

function uploadFailed(evt) {
  alert("There was an error attempting to upload the file.");
}

function uploadCanceled(evt) {
  alert("The upload has been canceled by the user or the browser dropped the connection.");
}

function setProcess(percent)
{
    document.getElementById('processPercent').innerHTML = 'Progress: ' + percent + '%';
    document.getElementById('progressNumber').innerHTML =
        '<div class="progress-bar" align = "middle" style="width: ' +
        percent + '%;">' + '</div>';
}
