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

    // set to "regular" by default; it's not what Chisel uses, but it's
    // probably the least surprising
    match.value = 'regular';
    // trigger the change event to disable the other options
    match.dispatchEvent(new Event('change'));
  });
  console.log('DOMContentLoaded');
});
