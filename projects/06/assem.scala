@main def main(file: String, others: String *) = {
    val lines = scala.io.Source.fromFile(file).getLines()
    val codes = lines.map(parse).toSeq
    val (symbols_label, _) = codes.foldLeft((default_symbols, 0)) { case ((symbols, instr_cnt), line) =>
        line match {
            case Empty() => (symbols, instr_cnt)
            case Label(name) => (symbols + (name -> instr_cnt), instr_cnt)
            case _ => (symbols, instr_cnt+1)
        }
    }
    val (symbols_full, _) = codes.foldLeft((symbols_label, 0)) { case ((symbols, reg_cnt), line) =>
        line match {
            case Empty() => (symbols, reg_cnt)
            case AInstruction(name) => name.toIntOption match {
                case None => if (symbols.contains(name)) {
                    (symbols, reg_cnt)
                } else {
                    (symbols + (name -> (16+reg_cnt)), reg_cnt+1)
                }
                case _ => (symbols, reg_cnt)
            }
            case _ => (symbols, reg_cnt)
        }
    }
    // println(symbols_full)
    val ml = codes.map {
        case AInstruction(name) => 
        val value = name.toIntOption.getOrElse(symbols_full(name))
        Some(value.toBinaryString.reverse.padTo(16, '0').reverse)
        case CInstruction(_dest, body, _jmp) => {
            val opcode = "111"
            val a = if (body.contains("M")) 1 else 0
            val jmp = _jmp match {
                case null => "000"
                case "JGT" => "001"
                case "JEQ" => "010"
                case "JGE" => "011"
                case "JLT" => "100"
                case "JNE" => "101"
                case "JLE" => "110"
                case "JMP" => "111"
            }
            val dest = _dest match {
                case null => "000"
                case "M" => "001"
                case "D" => "010"
                case "MD" => "011"
                case "A" => "100"
                case "AM" => "101"
                case "AD" => "110"
                case "AMD" => "111"
            }
            val unary = """([-!])?(\w)""".r
            val binary = """(\w)([-+&|])(\w)""".r
            val c = body match {
                case unary(op, operand) => (op, operand) match {
                    case (_, "0") => "101010"
                    case (neg, "1") => if (neg == "-") "111010" else "111111"
                    case (sym, "D") => sym match {
                        case null => "001100"
                        case "!" => "001101"
                        case "-" => "001111"
                    }
                    case (sym, _) => sym match {
                        case null => "110000"
                        case "!" => "110001"
                        case "-" => "110011"
                    }
                }
                case binary(lh, op, rh) => (lh, op, rh) match {
                    case ("D", "+", "1") => "011111"
                    case (_, "+", "1") => "110111"
                    case ("D", "-", "1") => "001110"
                    case (_, "-", "1") => "110010"
                    case ("D", "+", _) => "000010"
                    case ("D", "-", _) => "010011"
                    case (_, "-", "D") => "000111"
                    case ("D", "&", _) => "000000"
                    case ("D", "|", _) => "010101"
                }
            }
            Some(opcode + a + c + dest + jmp)
        }
        case _ => None
    }
    ml.foreach(_.foreach(println))
}



val empty = """\s*""".r
val label = """\((.*)\)""".r
val ainstr = """@(.*)""".r
val cinstr = """(([ADM]+)=)?(.+?)(;(\w+))?""".r
def parse(line: String): Line = line.split("//").head.trim match {
    case empty() => Empty()
    case label(name) => Label(name)
    case ainstr(name) => AInstruction(name)
    case cinstr(_,dest,body,_,jmp) => CInstruction(dest, body, jmp)
}

sealed class Line
case class Empty() extends Line
case class Label(name: String) extends Line
case class AInstruction(value: String) extends Line
case class CInstruction(dest: String, body: String, jmp: String) extends Line

val default_symbols = {
    val reg = (0 until 16).map(i => (s"R${i}" -> i)).toMap
    val predefined = Map(
        ("SP" -> 0),
        ("LCL" -> 1),
        ("ARG" -> 2),
        ("THIS" -> 3),
        ("THAT" -> 4),
        ("SCREEN" -> 16384),
        ("KBD" -> 24576),
    )
    reg ++ predefined
}