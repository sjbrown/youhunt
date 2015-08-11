<div
 style="background:#f0f0f0"
 ><h3>Choosing mission</h3>

${ c.get_potential_missions() }

${ c.id } ${ c }, your mission is to get a photo of:
<br />
<select>
% for m in c.get_potential_missions():
    <%
        print 'M', m
        prey = m.prey_Charactor__object
        print 'M', m
        stunt = MissionStunt.objects.get(id=m.stunt)
        base, additional = m.award_amounts()
        base_s = "%0.2f" % (base/100.0)
        additional_s = "%0.2f" % (additional/100.0)
    %>
    <option>${ prey |h} (${ prey.id }) Reward: $ ${base_s}
    % if additional:
        + $ ${additional_s}
    % endif
    </option>
% endfor
</select>

Doing stunt:
${ stunt }
<br />

<a href="some help text">How?</a>
<br />

<a href="${ make_url('client:charactor', c.id) }">I want a different mission</a>
<br />

I accept this mission:
<form action="${ make_url('api:charactor accept', c.id) }" method="post">
${ csrf }
<ul>
    <li><input id="accept_json" type=text name="accept_json"
         value='{"mission":"${m.id}"}'
         /></li>
    <li><input type="submit" />
    </li>
</ul>

</form>
</div>
