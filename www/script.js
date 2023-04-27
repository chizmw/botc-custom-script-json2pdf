const apiUrl =
  'https://cv2cfac6il.execute-api.eu-west-2.amazonaws.com/dev/render';

const dropzone = new Dropzone('#demo-upload', {
  url: apiUrl,
  previewTemplate: document.querySelector('#preview-template').innerHTML,
  parallelUploads: 2,
  thumbnailHeight: 120,
  thumbnailWidth: 120,
  maxFilesize: 5,
  filesizeBase: 1000,
  uploadMultiple: false,
  acceptedFiles: 'application/json',
  headers: {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'x-api-key': 'htmoQURLmm2MM0uTGV1s69EyReK3JReJ9XFwBWM2',
  },
  withCredentials: true,
  /*
  headers: {
    'Access-Control-Allow-Origin': '*', // Required for CORS support to work
    'Access-Control-Allow-Credentials': true, // Required for cookies, authorization headers with HTTPS
    'Access-Control-Allow-Headers':
      'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Content-Type': 'application/json',
  },
  */

  thumbnail: function (file, dataUrl) {
    if (file.previewElement) {
      file.previewElement.classList.remove('dz-file-preview');
      const images = file.previewElement.querySelectorAll(
        '[data-dz-thumbnail]'
      );
      for (const element of images) {
        let thumbnailElement = element;
        thumbnailElement.alt = file.name;
        thumbnailElement.src = dataUrl;
      }
      setTimeout(function () {
        file.previewElement.classList.add('dz-image-preview');
      }, 1);
    }
  },
});

// Now fake the file upload, since GitHub does not handle file uploads
// and returns a 404

const minSteps = 6,
  maxSteps = 60,
  timeBetweenSteps = 100,
  bytesPerStep = 100000;

dropzone._uploadFiles = function (files) {
  let self = this;

  for (const element of files) {
    let file = element;
    let totalSteps = Math.round(
      Math.min(maxSteps, Math.max(minSteps, file.size / bytesPerStep))
    );

    for (let step = 0; step < totalSteps; step++) {
      let duration = timeBetweenSteps * (step + 1);
      setTimeout(
        (function (file, totalSteps, step) {
          return function () {
            file.upload = {
              progress: (100 * (step + 1)) / totalSteps,
              total: file.size,
              bytesSent: ((step + 1) * file.size) / totalSteps,
            };

            self.emit(
              'uploadprogress',
              file,
              file.upload.progress,
              file.upload.bytesSent
            );
            if (file.upload.progress == 100) {
              file.status = Dropzone.SUCCESS;
              self.emit('success', file, 'success', null);
              self.emit('complete', file);
              self.processQueue();
            }
          };
        })(file, totalSteps, step),
        duration
      );
    }
  }
};
/* comment */
/* comment */
/* comment */
