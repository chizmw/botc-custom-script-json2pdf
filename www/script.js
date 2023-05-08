Dropzone.options.customScript = {
  url: API_GATEWAY_URL + '/render',
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

    this.on('error', (file, message, xhr) => {
      console.log('THERE WAS AN ERROR');
      console.log(xhr);
      console.error(message);
      console.log(file);
      if (file.previewElement) {
        file.previewElement.classList.add('dz-error');
        if (typeof message !== 'string' && message.error) {
          message = message.error;
        }
        for (let node of file.previewElement.querySelectorAll(
          '[data-dz-errormessage]'
        )) {
          node.textContent = message;
        }
      }
    });
  },
};
