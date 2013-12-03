function setInputValue(value, targetId) {
	//document.getElementById(targetId).setAttribute("value", value);
	$('#'+targetId).val(value);
}

function showHideAllAccounts(id) {
	$('tr[name="'+id+'"]').toggle();
}

function updateTransferDialog(address, balance, targetId) {
	if (targetId) {
		$('span#'+targetId+'_balance').html(balance);
		$('input#'+targetId).val(address);
	}
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
	      url: form.attr('action'),
	      data: form.serialize(),
	      dataType: 'json',
	      success: function( response ) {
	    	$('div#link_'+address+'>span').removeClass('faded');
	    	var tag_a = $('div#link_'+address+'>span>a');
	    	if (tag_a) {
	    		tag_a.html(response.alias);
	    	}
	        
	        $('div#edit_'+address).toggle(); 
	        $('div#link_'+address).toggle();
	      }
	    });
}

function editAlias (address) {
	var alias = $('div#link_'+address+'>span>a').html();
	$('input#new_alias_'+address).val(alias);
	$('div#edit_'+address).toggle();
	$('div#link_'+address).toggle();
	return false;
}

function setAlias (address, alias) {
	sendAddressAlias(address);
}

function updateQRImage(address) {
	$('img#qrthumb').attr('src', 'http://chart.apis.google.com/chart?chld=L|1&choe=ISO-8859-1&chs=300x300&cht=qr&chl='+address);
}