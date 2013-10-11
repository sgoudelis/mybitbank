function setInputValue(value, targetId) {
	document.getElementById(targetId).setAttribute("value", value);
}

function showHideAllAccounts(id) {
	$('tr[name="'+id+'"]').toggle()
	
}
