pics = ['https://encrypted-tbn2.google.com/images?q=tbn:ANd9GcSy4FJAXUIPTAPOOI_90LKada48k-jG_weoFEQg9x1vJiZSpcZuvtnecTU',
 'https://encrypted-tbn2.google.com/images?q=tbn:ANd9GcTsoWm0SV9eZC_X1SkCU-dZXzJj1qATXulz95JKFEjcgfaUpRGIJqfQBQ',
 'https://encrypted-tbn1.google.com/images?q=tbn:ANd9GcSqzp08TAr9rmg2CQC50cHbPMGnGrYo4ijy7ZZxBLG0taGQhQf-UiXWMe0S',
 'https://encrypted-tbn1.google.com/images?q=tbn:ANd9GcSdQDXsY7SGEa_AtB2qihOmceL6OWXGjbIEDvoz-8GOYz1AEx3292jOf6C7',
 'https://encrypted-tbn3.google.com/images?q=tbn:ANd9GcTtyVCPM7CtB5A5ViR4-3Td222oKBfTwrifr6NE3qtjQdEZ9N0vWzB5YS8I',
 'https://encrypted-tbn0.google.com/images?q=tbn:ANd9GcQ4LzNRpOB8814DdW-vilDU4fCXa8C3oo8iyPEFY1_b-Y27zCm2iMObqps',
 'https://encrypted-tbn2.google.com/images?q=tbn:ANd9GcQHIVb9s077jlYS-uydqU32PnU0ewXnM3NnWJDeKJDU2bpd46yBd2lK8gk',
 'https://encrypted-tbn2.google.com/images?q=tbn:ANd9GcTtduBhXw6EoxIFJeUEDtuw_iVkzp22w5ioMTxrwJ-ALRtP19JC0BwMm7M',
 'https://encrypted-tbn0.google.com/images?q=tbn:ANd9GcSgF9w7qAA4dHl-q8nPAP-3tRWvN6c18H5gLj4nUPucHt9rwHT4e9LqXYQ',
 'https://encrypted-tbn3.google.com/images?q=tbn:ANd9GcRp9kQpfyASqNzZOnIUrtxB8tu6zOM33mv6f5JPkVDOGeHIidNPbReB0Is']

$(function(){
    var $container = $('#profiles_list1');
//    $container.imagesLoaded( function(){
        $container.masonry({
            itemSelector : '.profile-item',
            isAnimated: true,
            isFitWidth: true,
        });
//    });
    $('#profile-pic').tooltip({
        'trigger': 'hover',
        'placement': 'right',
    })
    if ($("#img-selector").length > 0){
    $.each(pics, function(index, value) {
        $('#img-selector').append(
            $(document.createElement("li"))
                .addClass("selector-item")
                .append(
            $(document.createElement("img"))
                .attr({ src: value, title: 'image ' + index })
                .addClass("thumbnail")
                )
            )
        })};
});
