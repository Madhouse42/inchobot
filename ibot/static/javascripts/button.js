/**
 * Created with PyCharm.
 * User: ST
 * Date: 13-11-16
 * Time: 下午10:56
 * To change this template use File | Settings | File Templates.
 */

var delete_assignment = function (id) {
    $.post('/delete_assignment', {
        assignment_id: id
    }).done(function (data) {
                location.reload();
    });
};