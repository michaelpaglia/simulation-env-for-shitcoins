import { Tweet, TweetData } from './Tweet'
import styles from './Tweet.module.css'

interface TweetThreadProps {
  parent: TweetData
  replies: TweetData[]
  quotes: TweetData[]
}

export function TweetThread({ parent, replies, quotes }: TweetThreadProps) {
  return (
    <div className={styles.thread}>
      <Tweet tweet={parent} />

      {replies.map(reply => (
        <Tweet
          key={reply.id}
          tweet={reply}
          isReply
          replyToHandle={reply.reply_to_author || parent.author_handle}
        />
      ))}

      {quotes.map(quote => (
        <Tweet
          key={quote.id}
          tweet={quote}
          showQuoteEmbed
          quotedContent={quote.quoted_content || parent.content}
          quotedAuthor={quote.quoted_author || parent.author_handle}
        />
      ))}
    </div>
  )
}

/**
 * Groups an array of tweets into threads (parent with replies and quotes)
 */
export function groupTweetsIntoThreads(tweets: TweetData[]): TweetThreadProps[] {
  const tweetMap = new Map<string, TweetData>()
  const threads: TweetThreadProps[] = []
  const usedIds = new Set<string>()

  // Build tweet map
  tweets.forEach(t => tweetMap.set(t.id, t))

  // First pass: find parent tweets (original or quoted)
  tweets.forEach(tweet => {
    if (tweet.tweet_type === 'original' || !tweet.tweet_type) {
      threads.push({ parent: tweet, replies: [], quotes: [] })
      usedIds.add(tweet.id)
    }
  })

  // Second pass: attach replies and quotes to their parents
  tweets.forEach(tweet => {
    if (usedIds.has(tweet.id)) return

    if (tweet.tweet_type === 'reply' && tweet.is_reply_to) {
      const thread = threads.find(t => t.parent.id === tweet.is_reply_to)
      if (thread) {
        thread.replies.push(tweet)
        usedIds.add(tweet.id)
      }
    } else if (tweet.tweet_type === 'quote' && tweet.quotes_tweet) {
      const thread = threads.find(t => t.parent.id === tweet.quotes_tweet)
      if (thread) {
        thread.quotes.push(tweet)
        usedIds.add(tweet.id)
      }
    }
  })

  // Add any orphaned tweets as standalone
  tweets.forEach(tweet => {
    if (!usedIds.has(tweet.id)) {
      threads.push({ parent: tweet, replies: [], quotes: [] })
    }
  })

  return threads
}
