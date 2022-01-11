function toggle_like(dessert_name){
    let $a_like = $(`#${dessert_name} a[aria-label="heart"]`);
    let $i_like = $a_like.find("i")
    if($i_like.hasClass("fas")){
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                dessert_name_give: dessert_name,
                action_give: "unlike"
            },
            success: function(response){
                $i_like.addClass("far").removeClass("fas")
                $a_like.find("span.like-num").text(response["count"])
                window.location.reload()
            }
        })
    } else {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                dessert_name_give: dessert_name,
                action_give: "like"
            },
            success: function(response){
                $i_like.addClass("fas").removeClass("far")
                $a_like.find("span.like-num").text(response["count"])
                window.location.reload()
            }
        })
    }
}