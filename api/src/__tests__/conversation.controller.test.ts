import { Request, Response } from 'express'

const mockConversationCreate = jest.fn()
const mockConversationFindMany = jest.fn()
const mockConversationFindUnique = jest.fn()
const mockConversationDelete = jest.fn()
const mockDocumentFindUnique = jest.fn()

jest.mock('@prisma/client', () => ({
  PrismaClient: jest.fn().mockImplementation(() => ({
    conversation: {
      create: mockConversationCreate,
      findMany: mockConversationFindMany,
      findUnique: mockConversationFindUnique,
      delete: mockConversationDelete,
    },
    document: {
      findUnique: mockDocumentFindUnique,
    },
  })),
}))

import {
  createConversation,
  listConversations,
  deleteConversation,
} from '../controllers/conversation.controller'

const makeRes = () => {
  const res = {} as Response
  res.status = jest.fn().mockReturnValue(res)
  res.json = jest.fn().mockReturnValue(res)
  res.send = jest.fn().mockReturnValue(res)
  return res
}

describe('createConversation', () => {
  it('retorna 400 quando campos obrigatórios estão ausentes', async () => {
    const req = { body: { documentId: 'abc' } } as Request
    const res = makeRes()

    await createConversation(req, res)

    expect(res.status).toHaveBeenCalledWith(400)
    expect(res.json).toHaveBeenCalledWith({
      error: 'documentId, question e answer são obrigatórios.',
    })
  })

  it('retorna 404 quando o documento não existe', async () => {
    const req = {
      body: { documentId: 'inexistente', question: 'Pergunta?', answer: 'Resposta.' },
    } as Request
    const res = makeRes()
    mockDocumentFindUnique.mockResolvedValue(null)

    await createConversation(req, res)

    expect(res.status).toHaveBeenCalledWith(404)
    expect(res.json).toHaveBeenCalledWith({ error: 'Documento não encontrado.' })
  })

  it('cria a conversa e retorna 201', async () => {
    const req = {
      body: { documentId: 'doc-1', question: 'O que é RAG?', answer: 'É uma técnica...' },
    } as Request
    const res = makeRes()

    mockDocumentFindUnique.mockResolvedValue({ id: 'doc-1' })
    const fakeConversation = { id: 'conv-1', documentId: 'doc-1', question: 'O que é RAG?', answer: 'É uma técnica...' }
    mockConversationCreate.mockResolvedValue(fakeConversation)

    await createConversation(req, res)

    expect(mockConversationCreate).toHaveBeenCalledWith({
      data: { documentId: 'doc-1', question: 'O que é RAG?', answer: 'É uma técnica...' },
    })
    expect(res.status).toHaveBeenCalledWith(201)
    expect(res.json).toHaveBeenCalledWith(fakeConversation)
  })
})

describe('listConversations', () => {
  it('retorna 400 quando documentId não é fornecido', async () => {
    const req = { query: {} } as Request
    const res = makeRes()

    await listConversations(req, res)

    expect(res.status).toHaveBeenCalledWith(400)
    expect(res.json).toHaveBeenCalledWith({ error: 'Parâmetro documentId é obrigatório.' })
  })

  it('retorna as conversas do documento', async () => {
    const req = { query: { documentId: 'doc-1' } } as unknown as Request
    const res = makeRes()

    const fakeConversations = [
      { id: 'c1', question: 'P1', answer: 'R1' },
      { id: 'c2', question: 'P2', answer: 'R2' },
    ]
    mockConversationFindMany.mockResolvedValue(fakeConversations)

    await listConversations(req, res)

    expect(mockConversationFindMany).toHaveBeenCalledWith({
      where: { documentId: 'doc-1' },
      orderBy: { createdAt: 'asc' },
    })
    expect(res.json).toHaveBeenCalledWith(fakeConversations)
  })
})

describe('deleteConversation', () => {
  it('retorna 404 quando a conversa não existe', async () => {
    const req = { params: { id: 'inexistente' } } as unknown as Request
    const res = makeRes()
    mockConversationFindUnique.mockResolvedValue(null)

    await deleteConversation(req, res)

    expect(res.status).toHaveBeenCalledWith(404)
    expect(res.json).toHaveBeenCalledWith({ error: 'Conversa não encontrada.' })
  })

  it('deleta a conversa e retorna 204', async () => {
    const req = { params: { id: 'conv-1' } } as unknown as Request
    const res = makeRes()
    mockConversationFindUnique.mockResolvedValue({ id: 'conv-1' })

    await deleteConversation(req, res)

    expect(mockConversationDelete).toHaveBeenCalledWith({ where: { id: 'conv-1' } })
    expect(res.status).toHaveBeenCalledWith(204)
    expect(res.send).toHaveBeenCalled()
  })
})
