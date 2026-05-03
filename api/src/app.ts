import express from 'express'
import cors from 'cors'
import documentRoutes from './routes/document.routes'
import conversationRoutes from './routes/conversation.routes'

const app = express()

app.use(cors())
app.use(express.json())

app.use('/api/documents', documentRoutes)
app.use('/api/conversations', conversationRoutes)

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' })
})

export default app
