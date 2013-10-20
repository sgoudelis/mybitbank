function setInputValue(value, targetId) {
	//document.getElementById(targetId).setAttribute("value", value);
	$('#'+targetId).val(value);
}

function showHideAllAccounts(id) {
	$('tr[name="'+id+'"]').toggle()
	
}

function updateTransferDialog(address, balance, targetId) {
	$('span#'+targetId+'_balance').html(balance);
	$('input#'+targetId).val(address);
}