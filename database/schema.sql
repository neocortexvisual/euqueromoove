CREATE TABLE IF NOT EXISTS apoios (
  id UUID PRIMARY KEY,
  nome TEXT NOT NULL,
  instituicao TEXT NOT NULL,
  bairro TEXT NOT NULL,
  turno TEXT NOT NULL,
  faixa_etaria TEXT,
  curso TEXT,
  participacao JSONB NOT NULL,
  contato_apoio TEXT,
  contato_piloto TEXT,
  contato_embaixador TEXT,
  mensagem TEXT,
  relato_aprovado BOOLEAN NOT NULL DEFAULT FALSE,
  confirmou_piloto BOOLEAN NOT NULL,
  confirmou_independencia BOOLEAN NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

ALTER TABLE apoios
ADD COLUMN IF NOT EXISTS relato_aprovado BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE apoios
ADD COLUMN IF NOT EXISTS curso TEXT;

ALTER TABLE apoios
ALTER COLUMN faixa_etaria DROP NOT NULL;
