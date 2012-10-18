// js is ready if we need to do something dynamic
function addField(selector) {
	var n = $(selector+" input").length/2;
	$(selector).append('<input type="text" name="data_'+n+'_0" value="">')
	.append('<input type="text" name="data_'+n+'_1" value=""><br>');
}

$(function(){
	var data_selector = "#div_id_data div.controls";
	$("#add_field").click(function() {
		addField(data_selector);
		return false;
	});
	addField(data_selector);
});
