.mode tabs
.import llm_simulation_out.txt output 

update output set reply_num = null where reply_num = "";

with a as (
	select 
		post_id
		, reply_num
		, sum(case when vote = 1 then 1 else 0 end) as upvotes 
		, sum(case when vote = -1 then 1 else 0 end) as downvotes 
		, sum(case when vote = 0 then 1 else 0 end) as ignores
	from output
	group by post_id, reply_num
)
, counts as (
	select
		* 
		, cast(upvotes as float)/(upvotes + downvotes) as upvote_probability
		, cast(upvotes as float)/(upvotes + downvotes + ignores) as upvote_rate
	from a
)
, overall_counts as (
	select * from counts where reply_num is null
)
select 
	counts.post_id
	, counts.reply_num
	, counts.upvote_probability
	, counts.upvote_rate
	, overall_counts.upvote_probability as overall_upvote_probability
	, overall_counts.upvote_rate as overall_upvote_rate
	, abs(counts.upvote_probability - overall_counts.upvote_probability) / overall_counts.upvote_probability as upvote_probability_change_pct
	, abs(counts.upvote_rate - overall_counts.upvote_rate) / overall_counts.upvote_probability as upvote_rate_change_pct
from counts
join overall_counts on (counts.post_id = overall_counts.post_id)
where counts.reply_num is not null;