// js is ready if we need to do something dynamic
function addField(selector) {
	$(selector).append('<input type="text" name="json_key[data]" value=""> ')
	.append('<input type="text" name="json_value[data]" value=""><br>');
}

$(function(){
	$("#add_field").click(function() {
		addField("#form_data");
		return false;
	});
	addField("#form_data");
});
