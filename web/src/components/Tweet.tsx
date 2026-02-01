import { VerifiedBadge } from './icons'
import { TweetActions } from './TweetActions'
import styles from './Tweet.module.css'

export interface TweetData {
  id: string
  author_name: string
  author_handle: string
  author_type: string
  content: string
  hour: number
  likes: number
  retweets: number
  replies: number
  sentiment: number
  tweet_type?: 'original' | 'reply' | 'quote'
  is_reply_to?: string | null
  quotes_tweet?: string | null
  thread_depth?: number
  reply_to_author?: string | null
  quoted_content?: string | null
  quoted_author?: string | null
}

interface TweetProps {
  tweet: TweetData
  isReply?: boolean
  replyToHandle?: string
  showQuoteEmbed?: boolean
  quotedContent?: string
  quotedAuthor?: string
}

function getAvatarInitial(name: string): string {
  return name[0]?.toUpperCase() || '?'
}

function getAvatarColor(type: string): string {
  const colors: Record<string, string> = {
    kol: '#1d9bf0',
    degen: '#f91880',
    skeptic: '#f4212e',
    whale: '#ffd400',
    influencer: '#7856ff',
    normie: '#71767b',
    bot: '#00ba7c',
  }
  return colors[type] || '#71767b'
}

function isVerified(type: string): boolean {
  return ['kol', 'influencer', 'whale'].includes(type)
}

function isGoldVerified(type: string): boolean {
  return type === 'whale'
}

export function Tweet({
  tweet,
  isReply = false,
  replyToHandle,
  showQuoteEmbed = false,
  quotedContent,
  quotedAuthor,
}: TweetProps) {
  const tweetClasses = [styles.tweet]
  if (isReply) tweetClasses.push(styles.reply)

  return (
    <article className={tweetClasses.join(' ')}>
      {isReply && <div className={styles.threadLine} />}
      <div
        className={styles.avatar}
        style={{ background: getAvatarColor(tweet.author_type) }}
        aria-hidden="true"
      >
        {getAvatarInitial(tweet.author_name)}
      </div>
      <div className={styles.content}>
        {isReply && replyToHandle && (
          <div className={styles.replyIndicator}>
            Replying to <span className={styles.replyHandle}>@{replyToHandle}</span>
          </div>
        )}
        <div className={styles.header}>
          <span className={styles.name}>{tweet.author_name}</span>
          {isVerified(tweet.author_type) && (
            <VerifiedBadge gold={isGoldVerified(tweet.author_type)} />
          )}
          <span className={styles.handle}>@{tweet.author_handle}</span>
          <span className={styles.time}>· {tweet.hour}h</span>
          <span className={`${styles.typeBadge} ${styles[tweet.author_type] || ''}`}>
            {tweet.author_type}
          </span>
        </div>
        <div className={styles.text}>{tweet.content}</div>
        {showQuoteEmbed && quotedContent && (
          <div className={styles.quoteEmbed}>
            <div className={styles.quoteAuthor}>@{quotedAuthor}</div>
            <div className={styles.quoteContent}>{quotedContent}</div>
          </div>
        )}
        <TweetActions
          replies={tweet.replies}
          retweets={tweet.retweets}
          likes={tweet.likes}
        />
      </div>
    </article>
  )
}
