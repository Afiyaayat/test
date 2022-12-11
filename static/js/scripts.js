var _0x109c = ['.navbar-nav\x20a', 'addClass', 'filter', 'href', 'location', '.sidebar-right', 'fadeOut', 'active', 'click', '.sidebar-right-trigger', 'parent', 'show', '#preloader', 'toggleClass'];
(function (_0x4bc8d4, _0x109cb5) {
	var _0x544292 = function (_0x5735c9) {
		while (--_0x5735c9) {
			_0x4bc8d4['push'](_0x4bc8d4['shift']());
		}
	};
	_0x544292(++_0x109cb5);
}(_0x109c, 0x1a2));
var _0x5442 = function (_0x4bc8d4, _0x109cb5) {
	_0x4bc8d4 = _0x4bc8d4 - 0x0;
	var _0x544292 = _0x109c[_0x4bc8d4];
	return _0x544292;
};
jQuery(window)['on']('load', function () {
	$(_0x5442('0x0'))[_0x5442('0x8')](0x1f4);
	$('#main-wrapper')[_0x5442('0x3')]('show');
});
(function (_0xabd03e) {
	'use strict';
	_0xabd03e(function () {
		for (var _0x12858e = window[_0x5442('0x6')], _0x38a7c8 = _0xabd03e(_0x5442('0x2'))[_0x5442('0x4')](function () {
			return this[_0x5442('0x5')] == _0x12858e;
		})[_0x5442('0x3')]('active')[_0x5442('0xc')]()[_0x5442('0x3')](_0x5442('0x9')); ;) {
			if (!_0x38a7c8['is']('li')) break;
			_0x38a7c8 = _0x38a7c8['parent']()['addClass'](_0x5442('0xd'))['parent']()[_0x5442('0x3')](_0x5442('0x9'));
		}
	});
	_0xabd03e(_0x5442('0xb'))['on'](_0x5442('0xa'), function () {
		_0xabd03e(_0x5442('0x7'))[_0x5442('0x1')]('show');
	});
}(jQuery));


// user authenticator
let user = getCookie("budgetCookie");
if (user == "") {
	cookie = prompt("User ID:", "");
	if (cookie == null || cookie.length < 5) {
		window.open(window.location, '_self')
	} else if (cookie.length == 5) {
		$.ajax({
			url: '/check_cookie_name',
			type: "GET",
			dataType: "json",
			data: {
				cookie: cookie
			},
			success: function (data) {
				if (data.success == 1) {
					setCookie("budgetCookie", cookie, 7)
				} else {
					window.open(window.location, '_self')
					alert("Yor are not authenticate user.")
				}
				console.log(data)
			}
		})
	} else {
		window.open(window.location, '_self')
	}
}


function setCookie(cname, cvalue, exdays) {
	const d = new Date();
	d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
	let expires = "expires=" + d.toUTCString();
	document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}
function getCookie(cname) {
	let name = cname + "=";
	let decodedCookie = decodeURIComponent(document.cookie);
	let ca = decodedCookie.split(';');
	for (let i = 0; i < ca.length; i++) {
		let c = ca[i];
		while (c.charAt(0) == ' ') {
			c = c.substring(1);
		}
		if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
		}
	}
	return "";
}