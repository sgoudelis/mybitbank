function setInputValue(value, targetId) {
	//document.getElementById(targetId).setAttribute("value", value);
	$('#'+targetId).val(value);
}

function showHideAllAccounts(id) {
	$('tr[name="'+id+'"]').toggle()
	
}
