<h1>You Hunt! Web Client</h1>
<h2>Logged-in player charactor interface</h2>
Charactor: ${ c }
<br />
Activity: <b>${ c.activity }</b>
<br />
${ c._jdict }
<br />
<h3>Game ${ g.id } ${ g }
% if g.started:
    (Started)
% else:
    (Not started)
% endif
</h3>
<ul>
        % if getattr(c, 'current_judge_submissions', []):
            <%
                s_id = c.current_judge_submissions[0]
            %>
            <li><b>You are a Judge.
            <a href="${ make_url('client:charactor_submission', c.id, s_id)  }">See the photo</a>
            </b></li>
        % endif
        % if getattr(c, 'current_prey_submissions', []):
            <li><b>Someone has captured you!
            <a href="">See the photo they took</a>
            </b></li>
        % endif
        <li>Charactors ${ [str(x) for x in g.charactor_set.all()] }</li>


        % if not g.started:
            <li>Current invites ${ g.invites }
            <li>Invite players to game ${ g }
            % if start_allowed:
                <li><a href="${ make_url('api:game start', g.id) }"
                >Start game ${ g }</a>
            % endif
        % else:
            <li>
            % if c.activity == 'choosing_mission':
                <%include file='activity_choosing_mission.mako' />
            % endif
            % if c.activity == 'hunting':
                <%include file='activity_hunting.mako' />
            % endif
        % endif
</ul>


