// js is ready if we need to do something dynamic
$(function(){
	$("#add_field").click(function() {
		$("#form_data p").append('<input type="text" name="json_key[data]" value=""> <input type="text" name="json_value[data]" value=""><br>');
		return false;
	})
});
