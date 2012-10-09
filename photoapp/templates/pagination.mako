
<%def name="render_page_links(page)">
% if page.page_count > 1:
<div class="pagination">
    <ul>
        % if page.previous_page:
            <li><a href="${page_url(page.previous_page)}">&laquo;</a></li>
            {% else:
            <li class="disabled"><a href="#">&laquo;</a></li>
        % endif


        % for i in range(1, page.page_count + 1):

            % if i == page.page:
            <li class="disabled"><a href="#">${i}</a></li>
            % else:
            <li><a href="${page_url(i)}">${i}</a></li>
            % endif:

        % endfor

        % if page.next_page:
            <li class="next"><a href="${page_url(page.next_page)}">&raquo;</a></li>
            % else:
            <li class="disabled"><a href="#">&raquo;</a></li>
        % endif

    </ul>
</div>
% endif
</%def>
