import streamlit as st
import sqlite3
from datetime import datetime, date
from typing import List, Optional
import uuid
import json

# ⚠️ Deve ser a primeira chamada Streamlit
st.set_page_config(
    page_title="DesignConitiv — Gerenciador de Tarefas",
    layout="wide",
    page_icon="🗂️"
)

DB_PATH = "tasks_designconitiv.db"

# ------------------------- Helpers do banco -------------------------

def init_db(conn: sqlite3.Connection):
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            priority INTEGER NOT NULL,
            tags TEXT,
            due_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    conn.commit()

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    init_db(conn)
    return conn

def row_to_task(row):
    if row is None:
        return None
    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "status": row[3],
        "priority": row[4],
        "tags": row[5].split(",") if row[5] else [],
        "due_date": row[6],
        "created_at": row[7],
        "updated_at": row[8],
    }

def fetch_tasks(conn: sqlite3.Connection, where_clause: str = "", params: tuple = ()): 
    c = conn.cursor()
    query = "SELECT id, title, description, status, priority, tags, due_date, created_at, updated_at FROM tasks"
    if where_clause:
        query += " WHERE " + where_clause
    query += " ORDER BY priority ASC, due_date IS NULL, due_date ASC"
    c.execute(query, params)
    rows = c.fetchall()
    return [row_to_task(r) for r in rows]

def insert_task(conn: sqlite3.Connection, title: str, description: str, status: str, priority: int, tags: List[str], due_date: Optional[str]):
    c = conn.cursor()
    tid = str(uuid.uuid4())
    tags_str = ",".join([t.strip() for t in tags if t.strip()])
    now = datetime.utcnow().isoformat()
    c.execute('''INSERT INTO tasks(id, title, description, status, priority, tags, due_date, created_at)
                 VALUES(?,?,?,?,?,?,?,?)''', (tid, title, description, status, priority, tags_str, due_date, now))
    conn.commit()
    return tid

def update_task(conn: sqlite3.Connection, tid: str, **kwargs):
    allowed = ["title","description","status","priority","tags","due_date"]
    sets = []
    params = []
    for k, v in kwargs.items():
        if k in allowed:
            if k == "tags":
                v = ",".join([t.strip() for t in v if t.strip()])
            sets.append(f"{k} = ?")
            params.append(v)
    params.append(datetime.utcnow().isoformat())
    sets.append("updated_at = ?")
    params.append(tid)
    query = f"UPDATE tasks SET {', '.join(sets)} WHERE id = ?"
    c = conn.cursor()
    c.execute(query, tuple(params))
    conn.commit()

def delete_task(conn: sqlite3.Connection, tid: str):
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (tid,))
    conn.commit()

# ------------------------- Helpers da UI -------------------------

PRIORITY_LABELS = {1: "Baixa", 2: "Média", 3: "Alta", 4: "Urgente"}
STATUSES = ["A Fazer", "Em Progresso", "Bloqueada", "Concluída"]

def css():
    st.markdown(
        """
        <style>
        .app-header {display:flex; align-items:center; gap:12px}
        .brand {font-weight:700; font-size:22px}
        .card {background:linear-gradient(180deg, rgba(255,255,255,0.85), rgba(250,250,250,0.85));
               padding:12px; border-radius:12px; box-shadow: 0 6px 18px rgba(33,33,33,0.06);}
        .task-title {font-weight:600}
        .muted {color:#666; font-size:13px}
        .pill {display:inline-block; padding:6px 10px; border-radius:999px; background:#f1f3f5; margin-right:6px; font-size:12px}
        .kanban-col {min-height:120px}
        .priority-low {border-left:6px solid #84cc16}
        .priority-medium {border-left:6px solid #f59e0b}
        .priority-high {border-left:6px solid #ef4444}
        .priority-urgent {border-left:6px solid #7c3aed}
        </style>
        """,
        unsafe_allow_html=True,
    )

def small_stats(conn):
    tasks = fetch_tasks(conn)
    total = len(tasks)
    done = len([t for t in tasks if t["status"] == "Concluída"]) if tasks else 0
    overdue = 0
    today = date.today()
    for t in tasks:
        if t["due_date"]:
            try:
                d = datetime.fromisoformat(t["due_date"]).date()
                if d < today and t["status"] != "Concluída":
                    overdue += 1
            except Exception:
                pass
    cols = st.columns(3)
    cols[0].metric("Tarefas", total)
    cols[1].metric("Concluídas", done)
    cols[2].metric("Atrasadas", overdue)

# ------------------------- App -------------------------

conn = get_conn()
css()

# Cabeçalho
with st.container():
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    st.markdown('<div class="brand">🗂️ DesignConitiv</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Um gerenciador de tarefas agradável e focado em usabilidade</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# Sidebar: adicionar tarefa e filtros
with st.sidebar:
    st.header("Nova tarefa")
    title = st.text_input("Título", key="new_title")
    desc = st.text_area("Descrição (opcional)")
    col1, col2 = st.columns([2,1])
    with col1:
        priority = st.selectbox("Prioridade", options=[1,2,3,4], format_func=lambda x: PRIORITY_LABELS[x])
    with col2:
        status = st.selectbox("Status inicial", STATUSES, index=0)
    tags_input = st.text_input("Tags (separadas por vírgula)")
    due = st.date_input("Data de vencimento (opcional)", value=None)
    due_iso = due.isoformat() if isinstance(due, date) else None

    if st.button("Adicionar tarefa") and title.strip():
        tags = [t.strip() for t in tags_input.split(",")] if tags_input else []
        insert_task(conn, title.strip(), desc.strip(), status, priority, tags, due_iso)
        st.success("Tarefa adicionada")
        st.experimental_rerun()

    st.markdown("---")
    st.header("Filtrar")
    q = st.text_input("Pesquisar título/descrição/tags")
    st.selectbox("Filtrar por prioridade", options=["Todas","Baixa","Média","Alta","Urgente"], key="filter_priority")
    st.multiselect("Filtrar por status", options=STATUSES, key="filter_status", default=STATUSES)
    with st.expander("Avançado"):
        date_from = st.date_input("Vencimento a partir de", value=None, key="date_from")
        date_to = st.date_input("Vencimento até", value=None, key="date_to")

# Área principal: estatísticas + Kanban
small_stats(conn)

st.markdown("### Kanban")

# Filtro e busca
where_clauses = []
params = []
if q:
    where_clauses.append("(title LIKE ? OR description LIKE ? OR tags LIKE ?)")
    like_q = f"%{q}%"
    params.extend([like_q, like_q, like_q])

# filtro de prioridade
pfilter = st.session_state.get("filter_priority", "Todas")
if pfilter != "Todas":
    mapping = {"Baixa":1,"Média":2,"Alta":3,"Urgente":4}
    where_clauses.append("priority = ?")
    params.append(mapping[pfilter])

# filtro de status
sfilter = st.session_state.get("filter_status", STATUSES)
if sfilter:
    placeholders = ','.join('?' for _ in sfilter)
    where_clauses.append(f"status IN ({placeholders})")
    params.extend(list(sfilter))

# filtro por datas
if st.session_state.get("date_from"):
    where_clauses.append("due_date >= ?")
    params.append(st.session_state.get("date_from").isoformat())
if st.session_state.get("date_to"):
    where_clauses.append("due_date <= ?")
    params.append(st.session_state.get("date_to").isoformat())

where_clause = " AND ".join(where_clauses)
tasks = fetch_tasks(conn, where_clause, tuple(params))

# organizar por status
board = {s: [t for t in tasks if t["status"] == s] for s in STATUSES}

cols = st.columns(len(STATUSES))
for i, status_name in enumerate(STATUSES):
    with cols[i]:
        st.markdown(f"<div class='card kanban-col'><h4>{status_name} ({len(board[status_name])})</h4>", unsafe_allow_html=True)
        for t in board[status_name]:
            pr_class = "priority-low" if t["priority"] == 1 else ("priority-medium" if t["priority"]==2 else ("priority-high" if t["priority"]==3 else "priority-urgent"))
            due_str = f" — venc: {t['due_date'][:10]}" if t['due_date'] else ""
            tags_html = " ".join([f"<span class='pill'>{tag}</span>" for tag in t['tags']]) if t['tags'] else ""
            st.markdown(f"<div class='card {pr_class}' style='margin-bottom:10px;padding:10px;'>"
                        f"<div class='task-title'>{t['title']}</div>"
                        f"<div class='muted'>{t['description'][:140]}</div>"
                        f"<div style='margin-top:8px'>{tags_html}<span class='muted'>{PRIORITY_LABELS[t['priority']]}{due_str}</span></div>"
                        "</div>", unsafe_allow_html=True)
            cols_act = st.columns([1,1,1,1])
            if cols_act[0].button("▶️ Mover", key=f"move_{t['id']}"):
                try:
                    idx = STATUSES.index(t['status'])
                    new = STATUSES[min(idx+1, len(STATUSES)-1)]
                    update_task(conn, t['id'], status=new)
                    st.experimental_rerun()
                except Exception:
                    pass
            if cols_act[1].button("✅ Concluir", key=f"done_{t['id']}"):
                update_task(conn, t['id'], status="Concluída")
                st.experimental_rerun()
            if cols_act[2].button("✏️ Editar", key=f"edit_{t['id']}"):
                st.session_state['editing'] = t['id']
            if cols_act[3].button("🗑️", key=f"del_{t['id']}"):
                delete_task(conn, t['id'])
                st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Editor simples
if st.session_state.get('editing'):
    tid = st.session_state.get('editing')
    task = fetch_tasks(conn, "id = ?", (tid,))
    task = task[0] if task else None
    if task:
        with st.expander(f"Editar: {task['title']}", expanded=True):
            t_title = st.text_input("Título", value=task['title'], key="e_title")
            t_desc = st.text_area("Descrição", value=task['description'], key="e_desc")
            t_status = st.selectbox("Status", options=STATUSES, index=STATUSES.index(task['status']), key="e_status")
            t_priority = st.selectbox("Prioridade", options=[1,2,3,4], index=task['priority']-1, format_func=lambda x: PRIORITY_LABELS[x], key="e_prio")
            t_tags = st.text_input("Tags (vírgula)", value=",".join(task['tags']), key="e_tags")
            t_due = st.date_input("Vencimento (opcional)", value=datetime.fromisoformat(task['due_date']).date() if task['due_date'] else None, key="e_due")
            if st.button("Salvar alterações"):
                tags_list = [s.strip() for s in t_tags.split(",")] if t_tags else []
                due_iso = t_due.isoformat() if t_due else None
                update_task(conn, task['id'], title=t_title.strip(), description=t_desc.strip(), status=t_status, priority=t_priority, tags=tags_list, due_date=due_iso)
                st.session_state.pop('editing', None)
                st.success("Atualizado")
                st.experimental_rerun()
            if st.button("Cancelar"):
                st.session_state.pop('editing', None)
                st.experimental_rerun()

st.markdown("---")

# Import / Export
st.markdown("### Exportar / Importar")
col_imp, col_exp = st.columns(2)
with col_exp:
    if st.button("Exportar JSON"):
        tasks_all = fetch_tasks(conn)
        st.download_button("Download .json", data=json.dumps(tasks_all, ensure_ascii=False, indent=2), file_name="tasks_export.json")
with col_imp:
    uploaded = st.file_uploader("Importar JSON", type=["json"])
    if uploaded is not None:
        try:
            data = json.load(uploaded)
            for t in data:
                insert_task(conn, t.get('title','Sem título'), t.get('description',''), t.get('status','A Fazer'), int(t.get('priority',2)), t.get('tags',[]), t.get('due_date'))
            st.success("Importado")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Erro ao importar: {e}")

st.caption("DesignConitiv • criado para ser simples, agradável e produtivo — Luiz")
