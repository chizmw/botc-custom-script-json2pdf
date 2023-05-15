document.addEventListener('DOMContentLoaded', function () {
  tippy('.tippy-tip', {
    allowHTML: true,
    arrow: true,
    interactive: false,
    interactiveDebounce: 75,
    hideOnClick: true,
    trigger: 'click',
    placement: 'auto-end',
    touch: true,
  });

  /* if the select for EasyPrint is changed, enable/disable other options accordingly */
  /* react to onChange event for id=scriptFormat */
  document.querySelectorAll('#scriptFormat').forEach((match) => {
    match.addEventListener('change', (event) => {
      /* find the .needsEasyPrint class elements */
      document.querySelectorAll('.needs-easyprint').forEach((dependant) => {
        /* if the selected value is "EasyPrint" */
        if (event.target.value == 'easyprint') {
          /* enable the element */
          dependant.disabled = false;
        } else {
          /* disable the element */
          dependant.disabled = true;
        }
      });
    });
  });
  console.log('DOMContentLoaded');
});
