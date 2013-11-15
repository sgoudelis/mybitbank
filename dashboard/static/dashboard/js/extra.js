function setInputValue(value, targetId) {
	//document.getElementById(targetId).setAttribute("value", value);
	$('#'+targetId).val(value);
}

function showHideAllAccounts(id) {
	$('tr[name="'+id+'"]').toggle();
	
}

function updateTransferDialog(address, balance, targetId) {
	$('span#'+targetId+'_balance').html(balance);
	$('input#'+targetId).val(address);
}

function callAccountsOptionClick(selectElement) {
	optionElement = $(selectElement).find(":selected");
	if (optionElement.length) {
		$(optionElement).click();
	}
}

function sendAddressAlias(address) {
	var form = $('#set_alias_form_'+address);
	
	$.ajax({
	      type: "POST",
	      url: form.attr( 'action' ),
	      data: form.serialize(),
	      success: function( response ) {
	    	console.info('pipes');
	        $('div#link_'+address).html(response.alias);
	        $('div#edit_'+address).toggle(); 
	        $('div#link_'+address).toggle();
	      }
	    });
}
