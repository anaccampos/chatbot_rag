import { Request, Response } from 'express'

// Variáveis mock (prefixo 'mock' é obrigatório para o hoisting do Jest)
const mockDocumentCreate = jest.fn()
const mockDocumentFindMany = jest.fn()
const mockDocumentFindUnique = jest.fn()
const mockDocumentUpdate = jest.fn()
const mockDocumentDelete = jest.fn()
const mockFsExistsSync = jest.fn()
const mockFsUnlinkSync = jest.fn()

jest.mock('@prisma/client', () => ({
  PrismaClient: jest.fn().mockImplementation(() => ({
    document: {
      create: mockDocumentCreate,
      findMany: mockDocumentFindMany,
      findUnique: mockDocumentFindUnique,
      update: mockDocumentUpdate,
      delete: mockDocumentDelete,
    },
  })),
}))

jest.mock('fs', () => ({
  existsSync: mockFsExistsSync,
  unlinkSync: mockFsUnlinkSync,
}))

import {
  createDocument,
  listDocuments,
  getDocument,
  updateDocument,
  deleteDocument,
} from '../controllers/document.controller'

const makeRes = () => {
  const res = {} as Response
  res.status = jest.fn().mockReturnValue(res)
  res.json = jest.fn().mockReturnValue(res)
  res.send = jest.fn().mockReturnValue(res)
  return res
}

describe('createDocument', () => {
  it('retorna 400 quando nenhum arquivo é enviado', async () => {
    const req = { file: undefined } as Request
    const res = makeRes()

    await createDocument(req, res)

    expect(res.status).toHaveBeenCalledWith(400)
    expect(res.json).toHaveBeenCalledWith({ error: 'Nenhum arquivo enviado.' })
  })

  it('cria o documento e retorna 201', async () => {
    const fakeFile = { originalname: 'doc.pdf', path: '/uploads/doc.pdf' } as Express.Multer.File
    const req = { file: fakeFile } as Request
    const res = makeRes()

    const fakeDoc = { id: 'abc', filename: 'doc.pdf', filepath: '/uploads/doc.pdf', totalChunks: 0 }
    mockDocumentCreate.mockResolvedValue(fakeDoc)

    await createDocument(req, res)

    expect(mockDocumentCreate).toHaveBeenCalledWith({
      data: { filename: 'doc.pdf', filepath: '/uploads/doc.pdf', totalChunks: 0 },
    })
    expect(res.status).toHaveBeenCalledWith(201)
    expect(res.json).toHaveBeenCalledWith(fakeDoc)
  })
})

describe('listDocuments', () => {
  it('retorna a lista de documentos', async () => {
    const req = {} as Request
    const res = makeRes()

    const fakeDocs = [{ id: '1', filename: 'a.pdf' }, { id: '2', filename: 'b.pdf' }]
    mockDocumentFindMany.mockResolvedValue(fakeDocs)

    await listDocuments(req, res)

    expect(mockDocumentFindMany).toHaveBeenCalledWith({ orderBy: { createdAt: 'desc' } })
    expect(res.json).toHaveBeenCalledWith(fakeDocs)
  })
})

describe('getDocument', () => {
  it('retorna 404 quando o documento não existe', async () => {
    const req = { params: { id: 'inexistente' } } as unknown as Request
    const res = makeRes()
    mockDocumentFindUnique.mockResolvedValue(null)

    await getDocument(req, res)

    expect(res.status).toHaveBeenCalledWith(404)
    expect(res.json).toHaveBeenCalledWith({ error: 'Documento não encontrado.' })
  })

  it('retorna o documento quando encontrado', async () => {
    const req = { params: { id: 'abc' } } as unknown as Request
    const res = makeRes()
    const fakeDoc = { id: 'abc', filename: 'doc.pdf' }
    mockDocumentFindUnique.mockResolvedValue(fakeDoc)

    await getDocument(req, res)

    expect(res.json).toHaveBeenCalledWith(fakeDoc)
  })
})

describe('updateDocument', () => {
  it('retorna 404 quando o documento não existe', async () => {
    const req = { params: { id: 'inexistente' }, body: { totalChunks: 10 } } as unknown as Request
    const res = makeRes()
    mockDocumentFindUnique.mockResolvedValue(null)

    await updateDocument(req, res)

    expect(res.status).toHaveBeenCalledWith(404)
  })

  it('atualiza totalChunks e retorna o documento', async () => {
    const req = { params: { id: 'abc' }, body: { totalChunks: 15 } } as unknown as Request
    const res = makeRes()
    const fakeDoc = { id: 'abc', filename: 'doc.pdf', totalChunks: 15 }
    mockDocumentFindUnique.mockResolvedValue(fakeDoc)
    mockDocumentUpdate.mockResolvedValue(fakeDoc)

    await updateDocument(req, res)

    expect(mockDocumentUpdate).toHaveBeenCalledWith({ where: { id: 'abc' }, data: { totalChunks: 15 } })
    expect(res.json).toHaveBeenCalledWith(fakeDoc)
  })
})

describe('deleteDocument', () => {
  it('retorna 404 quando o documento não existe', async () => {
    const req = { params: { id: 'inexistente' } } as unknown as Request
    const res = makeRes()
    mockDocumentFindUnique.mockResolvedValue(null)

    await deleteDocument(req, res)

    expect(res.status).toHaveBeenCalledWith(404)
  })

  it('remove o arquivo do disco e o registro do banco', async () => {
    const req = { params: { id: 'abc' } } as unknown as Request
    const res = makeRes()
    const fakeDoc = { id: 'abc', filename: 'doc.pdf', filepath: '/uploads/doc.pdf' }
    mockDocumentFindUnique.mockResolvedValue(fakeDoc)
    mockFsExistsSync.mockReturnValue(true)

    await deleteDocument(req, res)

    expect(mockFsUnlinkSync).toHaveBeenCalledWith('/uploads/doc.pdf')
    expect(mockDocumentDelete).toHaveBeenCalledWith({ where: { id: 'abc' } })
    expect(res.status).toHaveBeenCalledWith(204)
    expect(res.send).toHaveBeenCalled()
  })
})
