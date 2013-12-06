// source http://stackoverflow.com/questions/149055/how-can-i-format-numbers-as-money-in-javascript
Number.prototype.formatMoney = function(c, d, t){
var n = this, 
    c = isNaN(c = Math.abs(c)) ? 2 : c, 
    d = d == undefined ? "." : d, 
    t = t == undefined ? "," : t, 
    s = n < 0 ? "-" : "", 
    i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "", 
    j = (j = i.length) > 3 ? j % 3 : 0;
   return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
 };

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

function editAlias(address) {
	var alias = $('div#link_'+address+'>span>a').html();
	$('input#new_alias_'+address).val(alias);
	$('div#edit_'+address).toggle();
	$('div#link_'+address).toggle();
	return false;
}

function setAlias(address, alias) {
	sendAddressAlias(address);
}

function updateQRImage(address) {
	$('img#qrthumb').attr('src', 'http://chart.apis.google.com/chart?chld=L|1&choe=ISO-8859-1&chs=300x300&cht=qr&chl='+address);
}

function convertAmounts(to, from) {
	// example format:  { code="USD", name="US Dollar", rate=1000.9482 }
	if (ratesUrl && ratesProxyUrl) {
		// get currency code keys
		if(from) {
			codes = [from]
		} else {
			//codes = Object.keys(ratesUrl);
			var codes = []; 
			
			$('span.currency').each(function(i, e) {
				codes.push($(e).html().toLowerCase());
			});
			
			var group = {};
			codes.map( function (a) { if (a in group) group[a] ++; else group[a] = 1; } );
			codes = Object.keys(group);
		}
		
		for(i in codes) {
			switch(codes[i])
			{
				// bitstamp
				case 'btc':
					$.ajax({
					    type: "POST",
					    url: ratesProxyUrl,
					    data: ratesUrl['btc_'+to.toLowerCase()],
					    success: function(json) {
							curr = {'code': "USD", 'name': "US Dollar", 'rate': json['last']}
							convertSpecificCurrencies('btc', curr);
					    },
					    error: function (xhr, textStatus, errorThrown) {
					        console.info("Could not retrieve currency rates fot BTC");
					    }
					});
					break;
				case 'ltc':
					$.ajax({
					    type: "POST",
					    url: ratesProxyUrl,
					    data: ratesUrl['ltc_'+to.toLowerCase()],
					    success: function(json) {
							curr = {'code': "USD", 'name': "US Dollar", 'rate': json['ticker']['last']}
							convertSpecificCurrencies('ltc', curr);
					    },
					    error: function (xhr, textStatus, errorThrown) {
					        console.info("Could not retrieve currency rates for LTC");
					    }
					});
					break;
				case 'ftc':
					$.ajax({
					    type: "POST",
					    url: ratesProxyUrl,
					    data: ratesUrl['ftc_'+to.toLowerCase()],
					    success: function(json) {
							curr = {'code': "USD", 'name': "US Dollar", 'rate': json['usd']}
							convertSpecificCurrencies('ftc', curr);
					    },
					    error: function (xhr, textStatus, errorThrown) {
					        console.info("Could not retrieve currency rates for FTC");
					    }
					});
				  break;
				case 'nmc':
					$.ajax({
					    type: "POST",
					    url: ratesProxyUrl,
					    data: ratesUrl['nmc_'+to.toLowerCase()],
					    success: function(json) {
							curr = {'code': "USD", 'name': "US Dollar", 'rate': json['last_trade']}
							convertSpecificCurrencies('nmc', curr);
					    },
					    error: function (xhr, textStatus, errorThrown) {
					        console.info("Could not retrieve currency rates for NMC");
					    }
					});
				  break;
				case 'nvc':
					$.ajax({
					    type: "POST",
					    url: ratesProxyUrl,
					    data: ratesUrl['nvc_'+to.toLowerCase()],
					    success: function(json) {
							curr = {'code': "USD", 'name': "US Dollar", 'rate': json['last_trade']}
							convertSpecificCurrencies('nvc', curr);
					    },
					    error: function (xhr, textStatus, errorThrown) {
					        console.info("Could not retrieve currency rates for NVC");
					    }
					});
				  break;
				case 'ppc':
					$.ajax({
					    type: "POST",
					    url: ratesProxyUrl,
					    data: ratesUrl['ppc_'+to.toLowerCase()],
					    success: function(json) {
							curr = {'code': "USD", 'name': "US Dollar", 'rate': json['last_trade']}
							convertSpecificCurrencies('ppc', curr);
					    },
					    error: function (xhr, textStatus, errorThrown) {
					        console.info("Could not retrieve currency rates for PPC");
					    }
					});
				  break;
			}
		}
	}
}

function convertSpecificCurrencies(from, to) {
	var amounts = $('span.amount.'+from).each(function(index, element){
		if(to) {
			var cryptoAmount = $(element).attr('amount');
			var converted = to.rate*cryptoAmount;
			var old_rate = $(element).attr('rate');
			//console.info(parseFloat(old_rate)+' <= '+to.rate+' '+(parseFloat(old_rate) <= to.rate));
			if(parseFloat(old_rate) <= to.rate) {
				$(element).addClass('green-font');
				$(element).removeClass('red-font');
			} else {
				$(element).addClass('red-font');
				$(element).removeClass('green-font');
			}
			$(element).html(converted.formatMoney(2));
			$(element).attr('rate', to.rate);
			$('span.currency-code.'+from).html(to.code);
		}
	});
}

