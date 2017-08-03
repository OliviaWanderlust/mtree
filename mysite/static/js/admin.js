function openWin(url){
    var url = url;      //转向网页的地址;  
    var iWidth = 1000;  //弹出窗口的宽度;  
    var iHeight = 550;  //弹出窗口的高度;  
    //获得窗口的垂直位置 
    var iTop = (window.screen.availHeight - 10 - iHeight) / 2; 
    //获得窗口的水平位置 
    var iLeft = (window.screen.availWidth - 10 - iWidth) / 2; 
    window.open(url, 'newwindow', 'height=' + iHeight + ',,innerHeight=' + iHeight + ',width=' + iWidth + ',innerWidth=' + iWidth + ',top=' + iTop + ',left=' + iLeft + ',status=no,toolbar=no,menubar=no,location=no,resizable=no,scrollbars=0,titlebar=no'); 
} 

$(document).ready(function(){
    //搜索
    $(".searchIpnutBtn").keydown(navList);
    function navList(e){
         if (e.which==13)//回车
         {
             $("#search-form").focus();
             var value = $.trim($(".searchIpnutBtn").val());
             var url = window.location.href.split("?")[0];
             url = url+"?key="+value;
             window.location.href = url;
         }
    }

	//导航
	$(".sideBar").find("li").bind('click',function(){
		$(this).siblings("li").removeClass("on");
		$(this).addClass("on");
		var nHei = $(this).find(".nav_2ji p").length*30;
		$(this).siblings("li").find(".nav_2ji").stop(true,true).animate({"height":0},500);
		$(this).find(".nav_2ji").stop(true,true).animate({"height":nHei},500);
		
	})
	var nHei0 = $(".sideBar").find("li.on").find(".nav_2ji p").length*30;
	$(".sideBar").find("li.on").find(".nav_2ji").css("height",nHei0);
	
	//TAB
	$(".jiguiTit li").bind('click',function(){
		var index = $(".jiguiTit li").index($(this));
		$(".jiguiTit li").removeClass("on");
		$(this).addClass("on");			
		$(".tabMain li").hide();
		$(".tabMain li").eq(index).show();
		//resieHeight();	
	});
	//弹层新增
	$(".popAdd,.popK").bind('click',function(){
        $(".tip").hide();
		$(".pop-1").show();	
		$(".popMask").show();
	});
	/*$(".popEdit,.popP").bind('click',function(){
		$(".pop-2").show();	
		$(".popMask").show();
	})*/
	$(".namePop,.popQ").bind('click',function(){
        $(".tip").hide();
		$(".pop-3").show();	
		$(".popMask").show();
	})
	
	//关闭
	$(".adminBox i,.cancel").bind('click',function(){
		$(".pop-1,.pop-2,.pop-3,.pop-4").hide();
		$(".popMask").hide();	
	});
	
	$(".checkAll").click(function(e) {
        var flag = $(this).attr("checked");
		var $checkBox = $(this).parents("table").find("tbody input[type=checkbox]");
		if(flag=="checked"){
			$checkBox.attr("checked","checked");
		}else{
			$checkBox.attr("checked",false);
		}
    });
	
	$(".detail").mouseenter(function(e){
		var top = e.pageY+10-$(window).scrollTop();;
		var left = e.pageX+10-$(window).scrollLeft();
		var text  = $(this).text();
		$(this).parents("table").next(".detailInfo").text(text).css({"top":top,"left":left}).show();
	});
	
	$(".detail").mouseleave(function(e){

		$(".detailInfo").hide().empty();
	});
	
    $("table tbody tr").each(function(index) {
        if(index%2==0){
            $(this).addClass("even");       
        }
    });
})
