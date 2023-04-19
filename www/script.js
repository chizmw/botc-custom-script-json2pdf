const dropZone = document.getElementById('drop_zone');
const apiUrl = 'https://chisel.malik-wright.uk/upload';

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  e.stopPropagation();
  dropZone.style.backgroundColor = '#f0f0f0';
});

dropZone.addEventListener('dragleave', (e) => {
  e.preventDefault();
  e.stopPropagation();
  dropZone.style.backgroundColor = '';
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  e.stopPropagation();
  dropZone.style.backgroundColor = '';

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    uploadFile(files[0]);
  }
});

async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      checkFinishedStatus(data.taskId);
    } else {
      console.error(
        'Error uploading file:',
        response.status,
        response.statusText
      );
    }
  } catch (error) {
    console.error('Error uploading file:', error);
  }
}

async function checkFinishedStatus(taskId) {
  const checkUrl = `https://your-api-endpoint.com/status/${taskId}`;

  let finished = false;
  while (!finished) {
    try {
      const response = await fetch(checkUrl);
      if (response.ok) {
        const data = await response.json();
        finished = data.finished;
        if (!finished) {
          setTimeout(() => {}, 3000); // Wait 3 seconds before polling again.
        } else {
          console.log('File processing finished:', data.result);
        }
      } else {
        console.error(
          'Error checking status:',
          response.status,
          response.statusText
        );
        break;
      }
    } catch (error) {
      console.error('Error checking status:', error);
      break;
    }
  }
}
