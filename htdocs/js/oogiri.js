// use jquery, jquery.json, jquery.cookie

(function() {
    // constants
    var display_array = ['#init_display', '#answer_display', '#vote_display', '#result_display'];
    var ranger_color = {'ルーキーブルー':'#7777FF', 'マンジレッド':'#FF7777', 'ミッコイエロー':'yellow', 'マリコピンク':'pink', 'チャンコグリーン':'#77FF77', 'ウーゴールド':'gold', 'ヨミチブラック':'#777777'};
    // variables
    var question;

    // initialize
    $(document).ready(function() {
	update_content(null);
	$('input[name="init.submit"]').click(submit_init);
	$('input[name="answer.submit"]').click(submit_answer);
	$('input[name="vote.submit"]').click(submit_vote);
    });

    // local functions
    function update_content(state) {
	var data = {
	    'state':state
	    , 'oogiri_name':$.cookie('oogiri_name')
	    , 'question_key':(question ? question.key : null)
	};
	$.ajax({
	    'type':'POST',
	    'contentType':'application/json',
 	    'processData':false,
 	    'url':'/oogiri/content',
 	    'data':$.toJSON(data),
 	    'dataType':'json',
 	    'success':update_content_callback
	});
    }

    function update_content_callback(data) {
	// data already converted to object
	var display_context = $(display_array[data.state]);
	// hide other displays
	display_context.siblings('.display').hide();

	if (data.state == 0) {
	    question = null;
	    update_init_display(data, display_context);
	} else if (data.state == 1) {
	    question = data.question;
	    update_answer_display(data, display_context);
	} else if (data.state == 2) {
	    update_vote_display(data, display_context);
	} else if (data.state == 3) {
	    question = null;
	    update_result_display(data, display_context);
	}
	display_context.show();
    }

    function update_init_display(data, context) {
	var total_counts = [0, 0];
	var voted_lists = [[], []]
	for (var i = 0, length = data.voted_counts.length; i < length; i++) {
	    var j = (data.voted_counts[i]['oogiri_name'] in ranger_color ? 0 : 1);
	    voted_lists[j].push(data.voted_counts[i]);
	    total_counts[j] += data.voted_counts[i]['count'];
	}
	$('#total_counts .gayarangers', context).text(total_counts[0]);
	$('#total_counts .citizens', context).text(total_counts[1]);
	var tbody = $('#total_counts > tbody', context);
	var voted_tr = $('> tr:last', tbody);
	voted_tr.remove();
	for (var i = 0, length = Math.max(voted_lists[0].length, voted_lists[1].length); i < length; i++) {
	    var tr = voted_tr.clone();
	    if (i < voted_lists[0].length) {
		var voted_count = voted_lists[0][i];
		$('td:nth-child(1) .oogiri_name', tr)
		    .text(voted_count['oogiri_name'])
		    .css('color', ranger_color[voted_count['oogiri_name']]);
		if (voted_count['oogiri_hash']) {
		    $('td:nth-child(1) .oogiri_hash', tr).text('#' + voted_count['oogiri_hash']);
		}
		$('td:nth-child(2)', tr).text(voted_count['count']);
	    }
	    if (i < voted_lists[1].length) {
		var voted_count = voted_lists[1][i];
		$('td:nth-child(3) .oogiri_name', tr).text(voted_count['oogiri_name']);
		if (voted_count['oogiri_hash']) {
		    $('td:nth-child(3) .oogiri_hash', tr).text('#' + voted_count['oogiri_hash']);
		}
		$('td:nth-child(4)', tr).text(voted_count['count']);
	    }
	    tbody.append(tr);
	}
	$('input[name="init.oogiri_name"]', context).val($.cookie('oogiri_name'));
	$('input[name="init.submit"]').siblings('img').hide();
    }

    function update_answer_display(data, context) {
	$('#question .oogiri_name', context)
	    .text(data.question.oogiri_name)
	    .css('color', ranger_color[data.question.oogiri_name]);
	$('#question .content', context).text(data.question.content);
	$('#answer .oogiri_name', context).text(data.oogiri_name);
	if (data.oogiri_hash) {
	    $('#answer .oogiri_hash', context).text('#' + data.oogiri_hash);
	}
	$('input[name="answer.content"]').val('');
	$('input[name="answer.submit"]').siblings('img').hide();
    }

    function update_vote_display(data, context) {
	$('#question .oogiri_name', context)
	    .text(data.question.oogiri_name)
	    .css('color', ranger_color[data.question.oogiri_name]);
	$('#question .content', context).text(data.question.content);
	// vote display
	var tbody = $('#answers > tbody', context);
	var answer_td = $('> tr > td:first', tbody);
	var vote_td = answer_td.next();
	$('input', vote_td).removeAttr('checked').removeAttr('disabled');
	// clear all rows
	tbody.empty();
	for (var i = 0, length = data.answers.length; i < length; i++) {
	    var tr = $('<tr/>');
	    tr.append(answer_td.clone().text(data.answers[i].content));
	    var td = vote_td.clone();
	    if (data.answers[i].oogiri_name || data.answers[i].oogiri_hash) {
		// my answer
		$('input', td).attr('disabled', true);
	    } else {
		$('input', td).val(data.answers[i].key);
	    }
	    tr.append(td);
	    tbody.append(tr);
	}
	$('input[name="vote.submit"]').siblings('img').hide();
    }

    function update_result_display(data, context) {
	var tbody = $('#voted_counts > tbody', context);
	var answer_oogiri_name_td = $('> tr > td:first', tbody);
	var my_voted_counts_td = answer_oogiri_name_td.next();
	// clear all rows
	tbody.empty();
	for (var i = 0, length = data.voted_counts.length; i < length; i++) {
	    var tr = $('<tr/>');
	    var td = answer_oogiri_name_td.clone();
	    $('.oogiri_name', td)
		.text(data.voted_counts[i].oogiri_name)
		.css('color', ranger_color[data.voted_counts[i].oogiri_name]);
	    if (data.voted_counts[i].oogiri_hash) {
		$('.oogiri_hash', td).text('#' + data.voted_counts[i].oogiri_hash);
	    }
	    tr.append(td);
	    tr.append(my_voted_counts_td.clone().text(data.voted_counts[i].count));
	    tbody.append(tr);
	}
    }

    function submit_init(event) {
	var oogiri_name = $('input[name="init.oogiri_name"]').val();
	if (!oogiri_name) {
	    return;
	}
	// save cookies
	$.cookie('oogiri_name', oogiri_name, {expires: 35});
	if (!$.cookie('oogiri_name')) {
	    $('input[name="init.oogiri_name"]').val('Cookie Off?');
	    return;
	}
	$('input[name="init.submit"]').siblings('img.loading').show();
	update_content(0);
    }

    function submit_answer(event) {
	// post an answer
	var answer = {};
	answer.question_key = question.key; // of currently displayed question
	// MSIE doesn't understand this form and returns undefined
	//var content = $('#answer_display #answer #content').val();
	answer.content = $('input[name="answer.content"]').val();
	if (!answer.content) {
	    return;
	}
	answer.oogiri_name = $.cookie('oogiri_name');

	$('input[name="answer.submit"]').siblings('img.loading').show();
	$.ajax({
	    'type':'POST',
	    'contentType':'application/json',
 	    'processData':false,
 	    'url':'/oogiri/answer',
 	    'data':$.toJSON(answer),
 	    'dataType':'json',
 	    'success':function(data) {
		update_content(1);
	    }
	});
    }

    function submit_vote(event) {
	// post a vote
	var vote = {};
	vote.question_key = question.key; // of currently displayed question
	vote.answer_key = $('input[name="vote.answer_key"]:checked').val();
	if (!vote.answer_key) {
	    return;
	}
	vote.oogiri_name = $.cookie('oogiri_name');

	$('input[name="vote.submit"]').siblings('img.loading').show();
	$.ajax({
	    'type':'POST',
	    'contentType':'application/json',
 	    'processData':false,
 	    'url':'/oogiri/vote',
 	    'data':$.toJSON(vote),
 	    'dataType':'json',
 	    'success':function(data) {
		update_content(2);
	    }
	});
    }
})();
