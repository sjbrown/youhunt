<div
 style="background:#f0f0f0"
 ><h3>Hunting</h3>

${ c.id } ${ c }, your mission is ${ c.human_readable_mission() }
<br />


Photo:
<form action="${ make_url('api:charactor submit', c.id) }" method="post">
${ csrf }
<ul>
    <li><input id="submit_json" type=text name="submit_json"
         value='{"photo_url":"http://i.imgur.com/L8GlJ3A.gif"}'
         /></li>
    <li><input type="submit" />
    </li>
</ul>

</form>
</div>

</div>
