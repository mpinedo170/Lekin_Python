from lekinpy import System, Job, Operation, Machine, Workcenter
from lekinpy import export_jobs_to_jobfile, export_workcenters_to_mchfile
from pathlib import Path

def test_export_accepts_whole_number_floats(tmp_path: Path):
    sys_ok = System()
    sys_ok.add_workcenter(Workcenter("W01", 0.0, "A", [Machine("A1", 0.0, "A")]))
    sys_ok.add_job(Job("J1", 0.0, 10.0, 1.0, [Operation("W01", 5.0, "A")]))
    job_path = tmp_path / "ok.job"
    mch_path = tmp_path / "ok.mch"
    export_jobs_to_jobfile(sys_ok, str(job_path))
    export_workcenters_to_mchfile(sys_ok, str(mch_path))
    assert "Release:            0" in job_path.read_text()
    assert "Oper:               W01;5;A" in job_path.read_text()
    assert "Release:            0" in mch_path.read_text()

def test_export_rejects_true_decimals(tmp_path: Path):
    sys_bad = System()
    sys_bad.add_workcenter(Workcenter("W02", 0, "A", [Machine("A2", 0, "A")]))
    sys_bad.add_job(Job("JX", 0, 10, 1, [Operation("W02", 5.5, "A")]))
    job_path = tmp_path / "bad.job"
    try:
        export_jobs_to_jobfile(sys_bad, str(job_path))
        assert False, "expected ValueError"
    except ValueError as e:
        assert "only integers" in str(e)
    assert not job_path.exists()