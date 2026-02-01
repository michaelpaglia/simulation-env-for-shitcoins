import { ReplyIcon, RepostIcon, LikeIcon, ViewsIcon, BookmarkIcon, ShareIcon } from './icons'
import styles from './Tweet.module.css'

interface TweetActionsProps {
  replies: number
  retweets: number
  likes: number
}

function formatNumber(n: number): string {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n.toString()
}

export function TweetActions({ replies, retweets, likes }: TweetActionsProps) {
  const views = Math.floor((likes + retweets) * 12.5)

  return (
    <div className={styles.actions}>
      <button
        className={`${styles.action} ${styles.actionReply}`}
        aria-label={`${replies} replies`}
        type="button"
      >
        <ReplyIcon />
        {replies > 0 && formatNumber(replies)}
      </button>
      <button
        className={`${styles.action} ${styles.actionRepost}`}
        aria-label={`${retweets} reposts`}
        type="button"
      >
        <RepostIcon />
        {retweets > 0 && formatNumber(retweets)}
      </button>
      <button
        className={`${styles.action} ${styles.actionLike}`}
        aria-label={`${likes} likes`}
        type="button"
      >
        <LikeIcon />
        {likes > 0 && formatNumber(likes)}
      </button>
      <button
        className={`${styles.action} ${styles.actionViews}`}
        aria-label={`${views} views`}
        type="button"
      >
        <ViewsIcon />
        {formatNumber(views)}
      </button>
      <button
        className={styles.action}
        aria-label="Bookmark"
        type="button"
      >
        <BookmarkIcon />
      </button>
      <button
        className={styles.action}
        aria-label="Share"
        type="button"
      >
        <ShareIcon />
      </button>
    </div>
  )
}
