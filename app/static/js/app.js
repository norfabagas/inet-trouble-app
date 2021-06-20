$( function () {
  if ($('#trouble').length > 0) {

    // disable input
    $('#trouble').attr('disabled', true);
    $('#trouble').val('Populating search suggestions...');

    fetchSuggestions().then((suggestions) => {
      $('#trouble').autocomplete({
        source: suggestions
      });

      // enable input
      $('#trouble').attr('disabled', false);
      $('#trouble').val('');
    })

  }
});

function fillForm(text, target) {
  $(`input[name=${target}]`).val(text);
}

async function fetchSuggestions() {
  let response = await fetch('/suggestions');

  if (!response.ok) {
    throw new Error(`HTTP Error, status: ${response.status}`);
  }

  return await response.json();
}