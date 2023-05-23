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
        if (
          event.target.value == 'easyprint' ||
          event.target.value == 'sample'
        ) {
          /* enable the element */
          dependant.disabled = false;
        } else {
          /* disable the element */
          dependant.disabled = true;
        }
      });
    });

    /* do something sensible if we haven't got a value in localStorage */
    if (!localStorage.getItem('scriptFormat')) {
      console.debug('✎ setting scriptFormat to sample');
      // set to "regular" by default; it's not what Chisel uses, but it's
      // probably the least surprising
      match.value = 'sample';

      // selector and default value to choose
      const defaults = {
        '#scriptFormat': 'sample',
        '#printFormat': 'doubleSided',
        '#playerNightInfo': 'yes',
        '#playerCount': 'sample',
      };

      // loop through the defaults and set them
      for (const [selector, value] of Object.entries(defaults)) {
        document.querySelector(selector).value = value;
        // match the item, store the value in localStorage, and trigger a change event
        let itemname = document.querySelector(selector).name;
        localStorage.setItem(itemname, value);
        document.querySelector(selector).dispatchEvent(new Event('change'));
      }
    }
  });

  /* set an event listener on each form element in the form id=customScript */
  document
    .querySelectorAll('#customScript input, #customScript select')
    .forEach((match) => {
      console.debug('✎ setting event listener for ' + match.name);

      /* if we have a value in localStorage for this element */
      if (localStorage.getItem(match.name)) {
        /* set the value of the element to the value in localStorage */
        match.value = localStorage.getItem(match.name);
        /* log the change */
        console.debug(
          '✅ setting ' + match.name + ' to ' + localStorage.getItem(match.name)
        );
      } else {
        /* say we didn't find a value in localStorage */
        console.debug('❌ no value found for ' + match.name);
      }

      /* when the element changes ... */
      match.addEventListener('change', (event) => {
        /* log the change */
        console.debug(
          '✎ ' + event.target.name + ' changed to ' + event.target.value
        );
        /* store the value in localStorage */
        localStorage.setItem(event.target.name, event.target.value);
      });
    });
  console.info('⭐ arcane scripts loaded…');
});
