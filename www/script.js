const apiUrl =
  'https://cv2cfac6il.execute-api.eu-west-2.amazonaws.com/dev/render';

//const dropzone = new Dropzone('#demo-upload', {
Dropzone.options.customScript = {
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
  //});
  //
  init: function () {
    this.on('success', (file) => {
      const obj = JSON.parse(file.xhr.response);
      console.log(obj);
      window.location.href = obj.url;
      // find span data-dz-name and replace with obj.url
      const span = file.previewElement.querySelector('[data-dz-name]');
      span.innerHTML =
        '<a href="' + obj.url + '" target="_blank">' + obj.script_name + '</a>';
      // hide .dz-size
      const dzsize = file.previewElement.querySelector('.dz-size');
      dzsize.innerHTML =
        '<span data-dz-size><img src="images/download.png" width="16" height="16"></span>';
    });
  },
};

// Now fake the file upload, since GitHub does not handle file uploads
// and returns a 404

/*
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
*/
/* comment */
/* comment */
/* comment */
