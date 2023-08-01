$("document").ready(function () {
    $.ajaxSetup({
        cache: false
    });
    $.ajax({
        url: document.URL,
        type: "GET",
        success: function (response) {
            var data = response;
            console.log(response)
            if (typeof (response) === "string") {
                $('#mapping_info').append(`<h2>${response}</h2>`);
            }
            for (const mapping of data) {

                var geneDiv = $('<div>').addClass('gene-info');
                // 创建一个<a>元素，用于触发折叠效果
                var buttonDiv = $('<div>').addClass('gene-button');
                //var geneInfo = $('<span>').text(mapping.hsp_info).css('font-size', '8px')
                var geneLink = $('<a>').text(mapping.hit_id).attr('href', document.location.origin + "/search_result/" + mapping.hit_id);
                var geneScore = $('<span>').text(mapping.hit_score).css('margin-left', '15px');
                var btn = $('<button>').attr("type", "button").attr("aria-label", "Left Align").addClass("btn btn-primary btn-xs").css('margin-right', '3px');

                var btn_inner = $('<span>').attr('aria-hidden', 'true').addClass("glyphicon glyphicon-minus");
                btn.append(btn_inner);
                btn.click(function (event) {
                    event.preventDefault();
                    $(this).parent().siblings('.mapping-seq').slideToggle();
                    btn_inner.toggleClass("glyphicon-minus glyphicon-plus");
                });
                // 创建一个<pre>元素，用于显示基因序列
                var geneSeq = $('<div>').addClass('mapping-seq').css('display', 'none');
                geneSeq.empty();
                for (const hsp of mapping.hsp_info) {
                    geneSeq.append(`<pre class='gene-seq'>${hsp}</pre>`);
                }
                // 将<a>元素和<pre>元素添加到<div>元素中
                buttonDiv.append(btn).append(geneLink).append(geneScore);
                geneDiv.append(buttonDiv).append(geneSeq);

                // 将<div>元素添加到页面中
                $('#mapping_info').append(geneDiv);

                //处理pre标签奇偶背景色不一样
                for (const i of $('.mapping-seq')) {
                    $(i).children('pre:odd').css('background', 'rgba(255,255,255,0.2)');
                }
            }
        },
        error: function (error) {
            console.log(error)
        },

    })
})